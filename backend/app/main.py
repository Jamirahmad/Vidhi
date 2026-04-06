from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import re
import time
import uuid
from collections import defaultdict, deque
from io import BytesIO
from pathlib import Path
from threading import Lock
from typing import Any, Awaitable, Callable, Dict, List, Optional
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, File, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.error_handlers import HttpError, install_exception_handlers
from backend.app.logging_config import configure_logging, get_logger, log_event
from backend.app.request_models import (
    FeedbackSubmitRequest,
    GenericAgentRequest,
    LiveSearchDrilldownRequest,
    LiveSearchRequest,
    ProvisionLookupRequest,
)
from backend.app.routes.system_routes import build_system_router
from backend.app.response_models import (
    FeedbackListResponse,
    FeedbackSubmitResponse,
    GenericDictResponse,
    GenericListItemResponse,
    HealthResponse,
    KnowledgeSearchItemResponse,
    LiveSearchDrilldownResponse,
    LiveSearchResponse,
    ProvisionLookupResponse,
    RefreshResponse,
)
from backend.app.services.prompt_service import resolve_system_prompt, resolve_task_prompt

try:
    from backend.app.knowledge import KnowledgeService
    KNOWLEDGE_IMPORT_ERROR: Optional[str] = None
except Exception as exc:
    KnowledgeService = None  # type: ignore[assignment]
    KNOWLEDGE_IMPORT_ERROR = str(exc)


ROOT_DIR = Path(__file__).resolve().parents[2]

for parent in [ROOT_DIR, *ROOT_DIR.parents]:
    env_file = parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        break

PORT = int(os.getenv("PORT", "8000"))
MODEL = os.getenv("VIDHI_LLM_MODEL") or os.getenv("VIDHI_OPENAI_MODEL") or "openai/gpt-4.1-mini"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "http://localhost:5173")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "Vidhi")
OPENROUTER_CHAT_URL = os.getenv("OPENROUTER_CHAT_URL", "https://openrouter.ai/api/v1/chat/completions")
OPENROUTER_MAX_TOKENS = int(os.getenv("OPENROUTER_MAX_TOKENS", "1800"))

REQUEST_LOGGER_NAME = "vidhi.request"
RATE_LIMIT_ENABLED = os.getenv("VIDHI_RATE_LIMIT_ENABLED", "true").strip().lower() in {"1", "true", "yes"}
RATE_LIMIT_WINDOW_S = max(1, int(os.getenv("VIDHI_RATE_LIMIT_WINDOW_S", "60")))
RATE_LIMIT_MAX_REQUESTS = max(1, int(os.getenv("VIDHI_RATE_LIMIT_MAX_REQUESTS", "120")))
RATE_LIMIT_BYPASS_PATHS = {
    path.strip()
    for path in os.getenv("VIDHI_RATE_LIMIT_BYPASS_PATHS", "/api/v1/health").split(",")
    if path.strip()
}
RESPONSE_CACHE_TTL_S = max(1, int(os.getenv("VIDHI_RESPONSE_CACHE_TTL_S", "300")))
RESPONSE_CACHE_MAX_ENTRIES = max(32, int(os.getenv("VIDHI_RESPONSE_CACHE_MAX_ENTRIES", "256")))
RESPONSE_STALE_TTL_S = max(1, int(os.getenv("VIDHI_RESPONSE_STALE_TTL_S", "900")))
PREWARM_QUERIES = [q.strip() for q in os.getenv("VIDHI_PREWARM_QUERIES", "bail,anticipatory bail,section 420,cheque bounce").split(",") if q.strip()]
PREWARM_ENABLED = os.getenv("VIDHI_PREWARM_ENABLED", "false").strip().lower() in {"1", "true", "yes"}
PREWARM_PROVISION_ENABLED = os.getenv("VIDHI_PREWARM_PROVISION_ENABLED", "false").strip().lower() in {"1", "true", "yes"}

KNOWLEDGE_SERVICE = None
KNOWLEDGE_INIT_ERROR: Optional[str] = None
if KnowledgeService is not None:
    try:
        KNOWLEDGE_SERVICE = KnowledgeService(ROOT_DIR)
    except Exception as exc:
        KNOWLEDGE_INIT_ERROR = str(exc)
else:
    KNOWLEDGE_INIT_ERROR = KNOWLEDGE_IMPORT_ERROR


configure_logging()
REQUEST_LOGGER = get_logger(REQUEST_LOGGER_NAME)

RATE_LIMIT_STORE: Dict[str, deque[float]] = defaultdict(deque)
RATE_LIMIT_LOCK = Lock()
RESPONSE_CACHE: Dict[str, tuple[float, Any]] = {}
RESPONSE_CACHE_LOCK = Lock()
RESPONSE_STALE_CACHE: Dict[str, tuple[float, Any]] = {}
CACHE_REFRESH_TASKS: set[str] = set()
CACHE_REFRESH_LOCK = Lock()
PROVISION_ANALYSIS_RESULTS: Dict[str, Dict[str, Any]] = {}
PROVISION_ANALYSIS_ERRORS: Dict[str, str] = {}
PROVISION_ANALYSIS_TASKS: set[str] = set()
PROVISION_ANALYSIS_LOCK = Lock()
PROVISION_URL_CACHE: Dict[str, str] = {}
PROVISION_URL_CACHE_LOCK = Lock()
PROVISION_URL_WARM_LIMIT = max(1, int(os.getenv("VIDHI_PROVISION_URL_WARM_LIMIT", "4")))


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        first = forwarded_for.split(",")[0].strip()
        if first:
            return first

    forwarded = request.headers.get("x-real-ip")
    if forwarded:
        return forwarded.strip()

    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def extract_first_match(pattern: str, text: str) -> str:
    match = re.search(pattern, text or "", flags=re.IGNORECASE)
    if not match:
        return ""
    return (match.group(1) or "").strip()


def extract_source_fields(content: str, fallback_url: str = "") -> Dict[str, str]:
    source_name = extract_first_match(r"Source:\s*(.+)", content)
    reference_url = extract_first_match(r"Reference URL:\s*(https?://\S+)", content)
    return {
        "sourceName": source_name or "Unknown Source",
        "sourceUrl": reference_url or (fallback_url or "").strip(),
    }


def is_provision_candidate(item: Dict[str, Any]) -> bool:
    category = str(item.get("category") or "").strip().lower()
    if category in {"provision", "statute"}:
        return True

    corpus = " ".join(
        [
            str(item.get("title") or ""),
            str(item.get("summary") or ""),
            str(item.get("content") or ""),
        ]
    ).lower()
    keywords = ("section", "article", "act", "code", "ipc", "bns", "crpc", "bnss")
    return any(keyword in corpus for keyword in keywords)


def compact_content_excerpt(content: str, limit_chars: int = 1200) -> str:
    text = re.sub(r"\s+", " ", (content or "").strip())
    if len(text) <= limit_chars:
        return text
    return text[:limit_chars].rstrip() + "..."


def _cache_copy(value: Any) -> Any:
    return json.loads(json.dumps(value))


def _response_cache_get(key: str) -> Optional[Any]:
    now = time.time()
    with RESPONSE_CACHE_LOCK:
        record = RESPONSE_CACHE.get(key)
        if not record:
            return None
        expires_at, value = record
        if expires_at < now:
            RESPONSE_CACHE.pop(key, None)
            return None
        return _cache_copy(value)


def _response_cache_set(key: str, value: Any, ttl_s: Optional[int] = None) -> None:
    now = time.time()
    effective_ttl = max(1, int(ttl_s if ttl_s is not None else RESPONSE_CACHE_TTL_S))
    with RESPONSE_CACHE_LOCK:
        if len(RESPONSE_CACHE) >= RESPONSE_CACHE_MAX_ENTRIES:
            expired = [k for k, (exp, _) in RESPONSE_CACHE.items() if exp < now]
            for item in expired:
                RESPONSE_CACHE.pop(item, None)
            if len(RESPONSE_CACHE) >= RESPONSE_CACHE_MAX_ENTRIES and RESPONSE_CACHE:
                oldest_key = min(RESPONSE_CACHE.items(), key=lambda item: item[1][0])[0]
                RESPONSE_CACHE.pop(oldest_key, None)
        RESPONSE_CACHE[key] = (now + effective_ttl, _cache_copy(value))
        RESPONSE_STALE_CACHE[key] = (now + max(effective_ttl, RESPONSE_STALE_TTL_S), _cache_copy(value))


def _response_cache_get_stale(key: str) -> Optional[Any]:
    now = time.time()
    with RESPONSE_CACHE_LOCK:
        record = RESPONSE_STALE_CACHE.get(key)
        if not record:
            return None
        expires_at, value = record
        if expires_at < now:
            RESPONSE_STALE_CACHE.pop(key, None)
            return None
        return _cache_copy(value)


def _schedule_cache_refresh(task_key: str, builder: Callable[[], Awaitable[Any]]) -> None:
    with CACHE_REFRESH_LOCK:
        if task_key in CACHE_REFRESH_TASKS:
            return
        CACHE_REFRESH_TASKS.add(task_key)

    async def _runner() -> None:
        try:
            await builder()
        except Exception:
            pass
        finally:
            with CACHE_REFRESH_LOCK:
                CACHE_REFRESH_TASKS.discard(task_key)

    asyncio.create_task(_runner())



def _provision_url_cache_key(title: str, source_url: str) -> str:
    return f"{(title or '').strip()}|{(source_url or '').strip()}"


def _get_cached_precise_provision_url(title: str, source_url: str) -> str:
    key = _provision_url_cache_key(title=title, source_url=source_url)
    with PROVISION_URL_CACHE_LOCK:
        return PROVISION_URL_CACHE.get(key, "")


def _set_cached_precise_provision_url(title: str, source_url: str, resolved_url: str) -> None:
    if not resolved_url:
        return
    key = _provision_url_cache_key(title=title, source_url=source_url)
    with PROVISION_URL_CACHE_LOCK:
        PROVISION_URL_CACHE[key] = resolved_url


async def _warm_precise_provision_url_cache(candidates: List[Dict[str, str]]) -> None:
    if not candidates:
        return

    for item in candidates[:PROVISION_URL_WARM_LIMIT]:
        title = str(item.get("title") or "")
        source_url = str(item.get("source_url") or "")
        if not title and not source_url:
            continue
        try:
            resolved = await resolve_precise_provision_url(title=title, source_url=source_url)
            if resolved:
                _set_cached_precise_provision_url(title=title, source_url=source_url, resolved_url=resolved)
        except Exception:
            continue

def _provision_analysis_job_id(query: str, facts: str, provisions: List[Dict[str, Any]]) -> str:
    raw = json.dumps(
        {
            "query": query,
            "facts": facts,
            "sources": [str(item.get("sourceId") or "") for item in provisions],
        },
        sort_keys=True,
    )
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:24]


async def _run_provision_analysis_job(job_id: str, query: str, facts: str, provisions: List[Dict[str, Any]]) -> None:
    try:
        llm_out = await llm_json(
            "provision_lookup",
            {
                "query": query,
                "facts": facts,
                "provisions": [
                    {
                        "sourceId": item.get("sourceId"),
                        "title": item.get("title"),
                        "summary": item.get("summary"),
                        "textExcerpt": item.get("textExcerpt"),
                        "sourceName": item.get("sourceName"),
                        "sourceUrl": item.get("sourceUrl"),
                    }
                    for item in provisions
                ],
            },
        )
        analysis_candidate = llm_out.get("analysis", {}) if isinstance(llm_out, dict) else {}
        if not isinstance(analysis_candidate, dict):
            analysis_candidate = {}
        with PROVISION_ANALYSIS_LOCK:
            PROVISION_ANALYSIS_RESULTS[job_id] = analysis_candidate
            PROVISION_ANALYSIS_ERRORS.pop(job_id, None)
    except Exception as exc:
        with PROVISION_ANALYSIS_LOCK:
            PROVISION_ANALYSIS_ERRORS[job_id] = str(exc)
    finally:
        with PROVISION_ANALYSIS_LOCK:
            PROVISION_ANALYSIS_TASKS.discard(job_id)


def resolve_reference_url(title: str, source_url: str, intent: str = "case_law") -> str:
    raw_url = (source_url or "").strip()
    if not raw_url:
        return ""

    parsed = urlparse(raw_url)
    if (parsed.path or "").strip() in {"", "/"}:
        return ""

    return raw_url


async def resolve_precise_provision_url(title: str, source_url: str) -> str:
    direct = resolve_reference_url(title=title, source_url=source_url, intent="provision")
    if direct:
        _set_cached_precise_provision_url(title=title, source_url=source_url, resolved_url=direct)
        return direct

    cached = _get_cached_precise_provision_url(title=title, source_url=source_url)
    if cached:
        return cached

    if KNOWLEDGE_SERVICE is None:
        return ""

    try:
        candidates = await KNOWLEDGE_SERVICE.live_web_search(query=title, limit=5, intent="provision")
    except Exception:
        return ""

    preferred = ""
    for item in candidates:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        if not url:
            continue
        parsed = urlparse(url)
        if (parsed.path or "").strip() in {"", "/"}:
            continue
        host = (parsed.netloc or "").lower()
        if "indiacode.nic.in" in host:
            _set_cached_precise_provision_url(title=title, source_url=source_url, resolved_url=url)
            return url
        if not preferred:
            preferred = url

    if preferred:
        _set_cached_precise_provision_url(title=title, source_url=source_url, resolved_url=preferred)
    return preferred

def normalize_provider_error(status: int, response_text: str) -> HttpError:
    if status in (401, 403):
        return HttpError(
            status=401,
            code="PROVIDER_AUTH_ERROR",
            message=f"OpenRouter authentication failed: {response_text}",
            user_message="OpenRouter authentication failed. Please verify OPENROUTER_API_KEY.",
        )

    if status == 402:
        return HttpError(
            status=402,
            code="PROVIDER_CREDITS_EXHAUSTED",
            message=f"OpenRouter credits exhausted: {response_text}",
            user_message="OpenRouter credits are insufficient for this request. Please add credits or use a lower-cost model.",
        )

    if status == 429:
        return HttpError(
            status=429,
            code="PROVIDER_RATE_LIMIT",
            message=f"OpenRouter rate limit: {response_text}",
            user_message="The AI provider is rate-limited right now. Please retry shortly.",
        )

    if status >= 500:
        return HttpError(
            status=502,
            code="PROVIDER_UPSTREAM_ERROR",
            message=f"OpenRouter upstream error: {response_text}",
            user_message="The AI provider is temporarily unavailable. Please retry in a few minutes.",
        )

    return HttpError(
        status=502,
        code="PROVIDER_ERROR",
        message=f"OpenRouter error {status}: {response_text}",
        user_message="The AI provider request failed. Please retry.",
    )


async def extract_text_from_upload(upload: UploadFile) -> str:
    data = await upload.read()
    if not data:
        raise HttpError(
            status=400,
            code="EMPTY_UPLOAD",
            message="Uploaded file is empty",
            user_message="Uploaded file is empty. Please upload a judgment copy with content.",
        )

    name = (upload.filename or "").lower()
    content_type = (upload.content_type or "").lower()

    try:
        if name.endswith(".pdf") or "pdf" in content_type:
            try:
                from pypdf import PdfReader
            except ModuleNotFoundError:
                raise HttpError(
                    status=503,
                    code="MISSING_PDF_PARSER",
                    message="pypdf is not installed",
                    user_message="PDF parser is missing on backend. Install dependencies and restart backend.",
                )
            reader = PdfReader(BytesIO(data))
            text_chunks = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(text_chunks).strip()

        if name.endswith(".docx") or "wordprocessingml" in content_type:
            try:
                from docx import Document as DocxDocument
            except ModuleNotFoundError:
                raise HttpError(
                    status=503,
                    code="MISSING_DOCX_PARSER",
                    message="python-docx is not installed",
                    user_message="DOCX parser is missing on backend. Install dependencies and restart backend.",
                )
            doc = DocxDocument(BytesIO(data))
            return "\n".join([paragraph.text for paragraph in doc.paragraphs]).strip()

        try:
            return data.decode("utf-8").strip()
        except UnicodeDecodeError:
            return data.decode("latin-1").strip()
    except HttpError:
        raise
    except Exception as exc:
        raise HttpError(
            status=400,
            code="UNSUPPORTED_UPLOAD",
            message=f"Failed to parse uploaded file: {exc}",
            user_message="Unsupported or unreadable file. Please upload PDF, DOCX, or TXT.",
        )


async def llm_json(task: str, payload: Dict[str, Any] | Any) -> Dict[str, Any]:
    if not OPENROUTER_API_KEY:
        raise HttpError(
            status=503,
            code="LLM_NOT_CONFIGURED",
            message="OPENROUTER_API_KEY is not set",
            user_message="AI service is not configured. Please ask your admin to add OPENROUTER_API_KEY.",
        )

    system_prompt = resolve_system_prompt()
    task_prompt = resolve_task_prompt(task)

    normalized_payload = payload.model_dump(mode="python") if hasattr(payload, "model_dump") else payload
    if not isinstance(normalized_payload, dict):
        normalized_payload = {"value": normalized_payload}

    request_payload = {
        "model": MODEL,
        "temperature": 0.2,
        "max_tokens": OPENROUTER_MAX_TOKENS,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "task": task_prompt,
                        "payload": normalized_payload,
                    }
                ),
            },
        ],
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": OPENROUTER_SITE_URL,
        "X-Title": OPENROUTER_APP_NAME,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(OPENROUTER_CHAT_URL, headers=headers, json=request_payload)

    if response.status_code >= 300:
        raise normalize_provider_error(response.status_code, response.text)

    data = response.json()
    content = (((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "{}")

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise HttpError(
            status=502,
            code="INVALID_PROVIDER_RESPONSE",
            message="LLM returned non-JSON content",
            user_message="AI response format was invalid. Please retry.",
        )


app = FastAPI(title="Vidhi Python Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limiter_middleware(request: Request, call_next):
    if not RATE_LIMIT_ENABLED or request.url.path in RATE_LIMIT_BYPASS_PATHS:
        return await call_next(request)

    now = time.time()
    ip = get_client_ip(request)

    with RATE_LIMIT_LOCK:
        history = RATE_LIMIT_STORE[ip]
        threshold = now - RATE_LIMIT_WINDOW_S
        while history and history[0] < threshold:
            history.popleft()

        if len(history) >= RATE_LIMIT_MAX_REQUESTS:
            retry_after = max(1, int(history[0] + RATE_LIMIT_WINDOW_S - now)) if history else RATE_LIMIT_WINDOW_S
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests",
                    "code": "RATE_LIMIT_EXCEEDED",
                    "userMessage": "Rate limit exceeded. Please retry shortly.",
                },
                headers={"Retry-After": str(retry_after)},
            )

        history.append(now)

    return await call_next(request)


@app.middleware("http")
async def request_logger_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    response.headers.setdefault("X-Request-Id", request_id)
    response.headers.setdefault("X-Backend-Latency-Ms", f"{duration_ms:.2f}")
    log_event(
        REQUEST_LOGGER,
        logging.INFO,
        "http_request",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=round(duration_ms, 2),
        client_ip=get_client_ip(request),
    )
    return response


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("X-XSS-Protection", "0")
    response.headers.setdefault("Content-Security-Policy", "default-src 'self'; frame-ancestors 'none'; base-uri 'self'")
    return response


app.state.request_logger = REQUEST_LOGGER
install_exception_handlers(app)

@app.on_event("startup")
async def prewarm_popular_queries() -> None:
    if KNOWLEDGE_SERVICE is None:
        return
    if not PREWARM_ENABLED and not PREWARM_PROVISION_ENABLED:
        return
    for query in PREWARM_QUERIES[:6]:
        cache_key_live = json.dumps(
            {"endpoint": "live-search", "query": query, "intent": "case_law", "limit": 5},
            sort_keys=True,
        )
        cache_key_provision = json.dumps(
            {"endpoint": "provision-lookup", "query": query, "facts": "", "limit": 5},
            sort_keys=True,
        )

        async def _warm_live(q: str = query, key: str = cache_key_live) -> None:
            try:
                response = await _build_live_search_response(query=q, intent="case_law", limit=5)
                _response_cache_set(key, response, ttl_s=RESPONSE_CACHE_TTL_S)
            except Exception:
                pass

        async def _warm_provision(q: str = query, key: str = cache_key_provision) -> None:
            try:
                response = await _build_provision_lookup_response(query=q, facts="", limit=5)
                ttl = RESPONSE_CACHE_TTL_S if response.get("analysisStatus") in {"ready", "error", "not_applicable"} else 5
                _response_cache_set(key, response, ttl_s=ttl)
            except Exception:
                pass

        if PREWARM_ENABLED:
            _schedule_cache_refresh(f"prewarm-live:{cache_key_live}", _warm_live)
        if PREWARM_PROVISION_ENABLED:
            _schedule_cache_refresh(f"prewarm-provision:{cache_key_provision}", _warm_provision)


_FEEDBACK_STORE: List[Dict[str, Any]] = []


async def _health_handler() -> HealthResponse:
    return {
        "status": "ok",
        "provider": "openrouter",
        "model": MODEL,
        "apiKeyConfigured": bool(OPENROUTER_API_KEY),
        "knowledge": {
            "provider": "langchain-chroma",
            "seedPath": str(ROOT_DIR / "backend" / "data" / "knowledge"),
            "publicSource": "https://www.sci.gov.in/",
            "available": KNOWLEDGE_SERVICE is not None,
            "error": KNOWLEDGE_INIT_ERROR,
        },
        "middleware": {
            "exceptionHandler": True,
            "requestLogger": True,
            "securityHeaders": True,
            "rateLimiter": {
                "enabled": RATE_LIMIT_ENABLED,
                "windowSeconds": RATE_LIMIT_WINDOW_S,
                "maxRequests": RATE_LIMIT_MAX_REQUESTS,
                "bypassPaths": sorted(list(RATE_LIMIT_BYPASS_PATHS)),
            },
        },
    }


async def _feedback_submit_handler(payload_dict: Dict[str, Any]) -> FeedbackSubmitResponse:
    payload = FeedbackSubmitRequest.model_validate(payload_dict)
    normalized_payload = payload.model_dump(mode="python")
    item = {
        "id": str(uuid.uuid4()),
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "payload": normalized_payload,
    }
    _FEEDBACK_STORE.append(item)
    return {"status": "received", "feedbackId": item["id"]}


async def _feedback_list_handler(limit: int) -> FeedbackListResponse:
    items = _FEEDBACK_STORE[-limit:]
    return {"count": len(items), "items": items}


app.include_router(
    build_system_router(
        health_handler=_health_handler,
        feedback_submit_handler=_feedback_submit_handler,
        feedback_list_handler=_feedback_list_handler,
    )
)


@app.get("/api/v1/knowledge-base/search")
async def knowledge_search(q: str = Query(..., min_length=2), limit: int = Query(12, ge=1, le=50)) -> List[KnowledgeSearchItemResponse]:
    if KNOWLEDGE_SERVICE is None:
        raise HttpError(
            status=503,
            code="KNOWLEDGE_SERVICE_UNAVAILABLE",
            message=f"Knowledge service failed to initialize: {KNOWLEDGE_INIT_ERROR}",
            user_message="Knowledge base is unavailable on backend startup. Please install backend dependencies and restart.",
        )
    return await KNOWLEDGE_SERVICE.search(query=q, limit=limit)


@app.post("/api/v1/knowledge-base/refresh")
async def knowledge_refresh(years: int = Query(5, ge=1, le=10), limit: int = Query(200, ge=10, le=500)) -> RefreshResponse:
    if KNOWLEDGE_SERVICE is None:
        raise HttpError(
            status=503,
            code="KNOWLEDGE_SERVICE_UNAVAILABLE",
            message=f"Knowledge service failed to initialize: {KNOWLEDGE_INIT_ERROR}",
            user_message="Knowledge base is unavailable on backend startup. Please install backend dependencies and restart.",
        )
    return await KNOWLEDGE_SERVICE.refresh_public_cases(years=years, limit=limit)


async def fetch_source_snapshot(url: str, max_chars: int = 5000) -> str:
    try:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            response = await client.get(url)
        if response.status_code >= 300:
            return ""
    except Exception:
        return ""

    content_type = str(response.headers.get("content-type") or "").lower()
    body = response.content or b""

    if "pdf" in content_type or url.lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(body))
            text = "\n".join([(page.extract_text() or "") for page in reader.pages[:6]])
            return compact_content_excerpt(text, limit_chars=max_chars)
        except Exception:
            return ""

    text = ""
    try:
        html = body.decode("utf-8", errors="ignore")
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        for node in soup(["script", "style", "noscript"]):
            node.extract()
        text = soup.get_text(" ", strip=True)
    except Exception:
        try:
            text = body.decode("utf-8", errors="ignore")
        except Exception:
            text = ""

    return compact_content_excerpt(text, limit_chars=max_chars)


@app.post("/api/v1/knowledge-base/live-search")
async def live_search(payload: LiveSearchRequest) -> LiveSearchResponse:
    if KNOWLEDGE_SERVICE is None:
        raise HttpError(
            status=503,
            code="KNOWLEDGE_SERVICE_UNAVAILABLE",
            message=f"Knowledge service failed to initialize: {KNOWLEDGE_INIT_ERROR}",
            user_message="Knowledge search is unavailable on backend startup. Please install backend dependencies and restart.",
        )

    query = payload.query.strip()
    intent = payload.intent.strip().lower()
    if intent not in {"case_law", "provision"}:
        intent = "case_law"

    limit = max(1, min(int(payload.limit), 20))
    cache_key = json.dumps({"endpoint": "live-search", "query": query, "intent": intent, "limit": limit}, sort_keys=True)
    cached = _response_cache_get(cache_key)
    if isinstance(cached, dict):
        return cached
    stale = _response_cache_get_stale(cache_key)
    if isinstance(stale, dict):
        async def _refresh_live_search() -> None:
            fresh = await _build_live_search_response(query=query, intent=intent, limit=limit)
            _response_cache_set(cache_key, fresh, ttl_s=RESPONSE_CACHE_TTL_S)

        _schedule_cache_refresh(f"live-search:{cache_key}", _refresh_live_search)
        return stale

    if len(query) < 2:
        raise HttpError(
            status=400,
            code="INVALID_QUERY",
            message="Search query is too short",
            user_message="Please enter a longer search query.",
        )

    response = await _build_live_search_response(query=query, intent=intent, limit=limit)
    _response_cache_set(cache_key, response, ttl_s=RESPONSE_CACHE_TTL_S)
    return response


async def _build_live_search_response(query: str, intent: str, limit: int) -> Dict[str, Any]:
    web_probe_count = 0
    if intent == "provision":
        web_probe = await KNOWLEDGE_SERVICE.live_web_search(query=query, limit=limit, intent="provision")
        web_probe_count = len(web_probe)
        hybrid_results = await KNOWLEDGE_SERVICE.hybrid_provision_search(query=query, limit=limit, web_limit=limit)
        results = []
        precise_url_cache: Dict[str, str] = {}
        for item in hybrid_results:
            title = str(item.get("title") or "")
            source_url = str(item.get("url") or "")
            direct_url = resolve_reference_url(title=title, source_url=source_url, intent="provision")
            if direct_url:
                exact_url = direct_url
            else:
                cache_url_key = f"{title}|{source_url}"
                if cache_url_key in precise_url_cache:
                    exact_url = precise_url_cache[cache_url_key]
                else:
                    exact_url = await resolve_precise_provision_url(title=title, source_url=source_url)
                    precise_url_cache[cache_url_key] = exact_url
            domain = urlparse(exact_url).netloc.lower() if exact_url else "local-kb"
            results.append(
                {
                    "id": str(item.get("id") or ""),
                    "intent": "provision",
                    "title": str(item.get("title") or "Legal source").strip(),
                    "snippet": str(item.get("snippet") or "").strip(),
                    "url": exact_url,
                    "domain": domain,
                    "publishedAt": str(item.get("publishedAt") or ""),
                    "source": str(item.get("source") or "local-kb"),
                }
            )
        search_source = "hybrid"
    else:
        results = await KNOWLEDGE_SERVICE.live_web_search(query=query, limit=limit, intent=intent)
        search_source = "searchapi"

        if not results:
            local_results = await KNOWLEDGE_SERVICE.search(query=query, limit=limit)
            mapped: List[Dict[str, Any]] = []
            for idx, item in enumerate(local_results[:limit]):
                source = extract_source_fields(
                    content=str(item.get("content") or ""),
                    fallback_url=str(item.get("source_url") or ""),
                )
                source_url = source.get("sourceUrl") or str(item.get("source_url") or "").strip()
                source_url = resolve_reference_url(title=str(item.get("title") or ""), source_url=source_url, intent=intent)
                domain = urlparse(source_url).netloc.lower() if source_url else "local-kb"
                mapped.append(
                    {
                        "id": str(item.get("id") or f"local-{intent}-{idx}"),
                        "intent": intent,
                        "title": str(item.get("title") or "Legal source").strip(),
                        "snippet": str(item.get("summary") or "Local knowledge match.").strip(),
                        "url": source_url,
                        "domain": domain,
                        "publishedAt": "",
                        "source": "local-kb",
                    }
                )
            results = mapped
            search_source = "local-fallback"

    source_breakdown: Dict[str, int] = {}
    for item in results:
        source_name = str(item.get("source") or "unknown")
        source_breakdown[source_name] = source_breakdown.get(source_name, 0) + 1

    return {
        "query": query,
        "intent": intent,
        "results": results,
        "count": len(results),
        "source": search_source,
        "sourceBreakdown": source_breakdown,
        "diagnostics": {
            "webConfigured": bool(getattr(KNOWLEDGE_SERVICE, "_searchapi_api_key", "")) if KNOWLEDGE_SERVICE else False,
            "webProvider": "searchapi",
            "webFetchedCount": web_probe_count if intent == "provision" else None,
            "webError": (KNOWLEDGE_SERVICE.get_last_web_error() if KNOWLEDGE_SERVICE and hasattr(KNOWLEDGE_SERVICE, "get_last_web_error") else "") if intent == "provision" else "",
        },
    }

@app.post("/api/v1/knowledge-base/provision-cache/clear")
async def clear_provision_cache() -> Dict[str, Any]:
    if KNOWLEDGE_SERVICE is None:
        raise HttpError(
            status=503,
            code="KNOWLEDGE_SERVICE_UNAVAILABLE",
            message=f"Knowledge service failed to initialize: {KNOWLEDGE_INIT_ERROR}",
            user_message="Knowledge search is unavailable on backend startup. Please install backend dependencies and restart.",
        )

    deleted = KNOWLEDGE_SERVICE.clear_cached_provision_results()
    return {
        "deleted": deleted,
        "status": "ok",
    }


@app.post("/api/v1/knowledge-base/live-search/drilldown")
async def live_search_drilldown(payload: LiveSearchDrilldownRequest) -> LiveSearchDrilldownResponse:
    query = payload.query.strip()
    objective = payload.objective.strip()

    selected = [item.model_dump(mode="python") for item in payload.selected]
    cache_key = json.dumps(
        {"endpoint": "live-search-drilldown", "query": query, "objective": objective, "selected": selected},
        sort_keys=True,
    )
    cached = _response_cache_get(cache_key)
    if isinstance(cached, dict):
        return cached

    normalized_sources: List[Dict[str, str]] = []
    for idx, item in enumerate(selected):
        if not isinstance(item, dict):
            continue
        source_id = str(item.get("id") or f"source-{idx+1}")
        title = str(item.get("title") or "Legal source").strip()
        url = str(item.get("url") or "").strip()
        snippet = str(item.get("snippet") or "").strip()
        normalized_sources.append(
            {
                "id": source_id,
                "title": title,
                "url": url,
                "snippet": snippet,
            }
        )

    if not normalized_sources:
        raise HttpError(
            status=400,
            code="NO_SOURCES_SELECTED",
            message="No sources selected for drilldown",
            user_message="Select at least one source before running drilldown.",
        )

    async def enrich_source(source: Dict[str, str]) -> Dict[str, Any]:
        extracted = await fetch_source_snapshot(source["url"], max_chars=5000) if source["url"] else ""
        if not extracted:
            extracted = compact_content_excerpt(
                " ".join(
                    [
                        source.get("title") or "",
                        source.get("snippet") or "",
                        "No direct source URL available for full-text extraction.",
                    ]
                ),
                limit_chars=1200,
            )
        return {
            "id": source["id"],
            "title": source["title"],
            "url": source["url"],
            "snippet": source["snippet"],
            "extractedText": extracted,
        }

    enriched_sources = await asyncio.gather(*[enrich_source(source) for source in normalized_sources[:8]])

    analysis: Optional[Dict[str, Any]] = None
    analysis_error: Optional[str] = None
    allowed_ids = {src["id"] for src in enriched_sources}

    if OPENROUTER_API_KEY:
        try:
            out = await llm_json(
                "knowledge_drilldown",
                {
                    "query": query,
                    "objective": objective,
                    "sources": enriched_sources,
                },
            )
            candidate = out.get("analysis", {}) if isinstance(out, dict) else {}
            if isinstance(candidate, dict):
                cited = candidate.get("citedSourceIds", [])
                if not isinstance(cited, list):
                    cited = []
                candidate["citedSourceIds"] = [sid for sid in cited if str(sid) in allowed_ids]

                notes = candidate.get("citationNotes", [])
                if isinstance(notes, list):
                    candidate["citationNotes"] = [
                        note
                        for note in notes
                        if isinstance(note, dict) and str(note.get("sourceId") or "") in allowed_ids
                    ]
                else:
                    candidate["citationNotes"] = []
                analysis = candidate
        except Exception as exc:
            analysis_error = str(exc)

    response = {
        "query": query,
        "objective": objective,
        "sources": enriched_sources,
        "analysis": analysis,
        "analysisError": analysis_error,
        "grounding": {
            "strictSourceValidation": True,
            "allowedSourceIds": sorted(list(allowed_ids)),
        },
    }
    _response_cache_set(cache_key, response, ttl_s=300)
    return response


def _cache_retrieved_provisions_to_rag(query: str, facts: str, provisions: List[Dict[str, Any]]) -> None:
    if not provisions or KNOWLEDGE_SERVICE is None:
        return

    pipeline = getattr(KNOWLEDGE_SERVICE, "_pipeline", None)
    store = getattr(pipeline, "store", None)
    add_cases = getattr(store, "add_cases", None)
    if not callable(add_cases):
        return

    docs: List[Dict[str, Any]] = []
    today = time.strftime("%Y-%m-%d")

    for item in provisions:
        title = str(item.get("title") or "Legal provision").strip()
        summary = str(item.get("summary") or "").strip()
        excerpt = str(item.get("textExcerpt") or "").strip()
        source_url = str(item.get("sourceUrl") or "").strip()
        source_name = str(item.get("sourceName") or "Provision Lookup Pipeline").strip()

        stable = f"{title}|{source_url}|{summary[:200]}"
        doc_id = "lookup-provision-" + hashlib.sha256(stable.encode("utf-8")).hexdigest()[:24]

        docs.append(
            {
                "id": doc_id,
                "title": title,
                "category": "provision",
                "summary": summary,
                "text": "\n\n".join(
                    [
                        excerpt or summary or title,
                        f"Source: {source_name}",
                        f"Reference URL: {source_url}" if source_url else "",
                        f"Query: {query}",
                        f"Facts: {facts}" if facts else "",
                        f"Updated: {today}",
                    ]
                ).strip(),
                "source_name": source_name,
                "source_url": source_url,
                "authority": "Provision Lookup Pipeline",
                "jurisdiction": "India",
                "tags": ["provision", "lookup", "cached", "rag"],
                "updated_at": today,
            }
        )

    try:
        add_cases(docs)
    except Exception:
        return

@app.post("/api/v1/knowledge-base/provision-lookup")
async def provision_lookup(payload: ProvisionLookupRequest) -> ProvisionLookupResponse:
    if KNOWLEDGE_SERVICE is None:
        raise HttpError(
            status=503,
            code="KNOWLEDGE_SERVICE_UNAVAILABLE",
            message=f"Knowledge service failed to initialize: {KNOWLEDGE_INIT_ERROR}",
            user_message="Knowledge base is unavailable on backend startup. Please install backend dependencies and restart.",
        )

    query = payload.query.strip()
    facts = payload.facts.strip()
    limit = max(1, min(int(payload.limit), 12))
    start_analysis = bool(payload.startAnalysis)
    cache_key = json.dumps({"endpoint": "provision-lookup", "query": query, "facts": facts, "limit": limit, "startAnalysis": start_analysis}, sort_keys=True)
    cached = _response_cache_get(cache_key)
    if isinstance(cached, dict):
        return cached
    stale = _response_cache_get_stale(cache_key)
    if isinstance(stale, dict):
        async def _refresh_provision_lookup() -> None:
            refreshed = await _build_provision_lookup_response(query=query, facts=facts, limit=limit, start_analysis=start_analysis)
            ttl = RESPONSE_CACHE_TTL_S if refreshed.get("analysisStatus") in {"ready", "error", "not_applicable"} else 5
            _response_cache_set(cache_key, refreshed, ttl_s=ttl)

        _schedule_cache_refresh(f"provision-lookup:{cache_key}", _refresh_provision_lookup)
        return stale

    if len(query) < 2:
        raise HttpError(
            status=400,
            code="INVALID_QUERY",
            message="Provision lookup query is too short",
            user_message="Please enter a longer query for legal provision lookup.",
        )

    response = await _build_provision_lookup_response(query=query, facts=facts, limit=limit, start_analysis=start_analysis)
    ttl = RESPONSE_CACHE_TTL_S if response.get("analysisStatus") in {"ready", "error", "not_applicable"} else 5
    _response_cache_set(cache_key, response, ttl_s=ttl)
    return response


async def _build_provision_lookup_response(query: str, facts: str, limit: int, start_analysis: bool = False) -> Dict[str, Any]:
    search_query = " ".join([query, facts]).strip()
    local_results = await KNOWLEDGE_SERVICE.search_provisions(query=search_query, limit=max(limit * 2, 12))
    scoped_results = [item for item in local_results if is_provision_candidate(item)]

    provisions: List[Dict[str, Any]] = []
    warm_candidates: List[Dict[str, str]] = []
    for item in scoped_results[:limit]:
        source = extract_source_fields(
            content=str(item.get("content") or ""),
            fallback_url=str(item.get("source_url") or ""),
        )
        title = str(item.get("title") or "")
        source_url = str(source["sourceUrl"])

        direct_url = resolve_reference_url(title=title, source_url=source_url, intent="provision")
        cached_url = _get_cached_precise_provision_url(title=title, source_url=source_url) if not direct_url else ""
        resolved_source_url = direct_url or cached_url

        if not resolved_source_url and source_url:
            warm_candidates.append({"title": title, "source_url": source_url})

        provisions.append(
            {
                "sourceId": str(item.get("id") or ""),
                "title": title.strip(),
                "category": str(item.get("category") or "").strip(),
                "summary": str(item.get("summary") or "").strip(),
                "textExcerpt": compact_content_excerpt(str(item.get("content") or "")),
                "sourceName": source["sourceName"],
                "sourceUrl": resolved_source_url,
            }
        )

    if warm_candidates:
        asyncio.create_task(_warm_precise_provision_url_cache(warm_candidates))

    _cache_retrieved_provisions_to_rag(query=query, facts=facts, provisions=provisions)

    if not provisions:
        return {
            "query": query,
            "facts": facts,
            "provisions": [],
            "analysis": None,
            "analysisError": None,
            "analysisStatus": "not_applicable",
            "analysisJobId": None,
            "grounding": {"strictSourceValidation": True, "allowedSourceIds": []},
            "retrievalDiagnostics": {
                "ragCount": 0,
                "webCount": 0,
                "hybridCount": 0,
                "seedCount": 0,
                "llmScoutCount": 0,
                "webError": KNOWLEDGE_SERVICE.get_last_web_error() if KNOWLEDGE_SERVICE and hasattr(KNOWLEDGE_SERVICE, "get_last_web_error") else "",
                "pipeline": ["rag_local"],
            },
        }

    source_name_counts: Dict[str, int] = {}
    for item in provisions:
        source_name = str(item.get("sourceName") or "unknown").strip().lower()
        source_name_counts[source_name] = source_name_counts.get(source_name, 0) + 1

    web_count = sum(count for name, count in source_name_counts.items() if "searchapi" in name or "web" in name)
    llm_scout_count = sum(count for name, count in source_name_counts.items() if "llm" in name or "scout" in name)
    rag_count = max(0, len(provisions) - web_count - llm_scout_count)

    pipeline: List[str] = ["rag_local"]
    if web_count > 0:
        pipeline.append("searchapi_cached")
    if llm_scout_count > 0:
        pipeline.append("llm_scout")

    allowed_source_ids = {str(item.get("sourceId") or "") for item in provisions}
    job_id = _provision_analysis_job_id(query=query, facts=facts, provisions=provisions)
    analysis: Optional[Dict[str, Any]] = None
    analysis_error: Optional[str] = None
    analysis_status = "pending"

    with PROVISION_ANALYSIS_LOCK:
        if job_id in PROVISION_ANALYSIS_RESULTS:
            analysis_status = "ready"
            analysis = _cache_copy(PROVISION_ANALYSIS_RESULTS[job_id])
        elif job_id in PROVISION_ANALYSIS_ERRORS:
            analysis_status = "error"
            analysis_error = PROVISION_ANALYSIS_ERRORS[job_id]
        elif job_id in PROVISION_ANALYSIS_TASKS:
            analysis_status = "pending"
        elif not start_analysis:
            analysis_status = "not_started"
        elif not OPENROUTER_API_KEY:
            analysis_status = "disabled"
        else:
            PROVISION_ANALYSIS_TASKS.add(job_id)
            asyncio.create_task(_run_provision_analysis_job(job_id, query, facts, provisions))

    if isinstance(analysis, dict):
        cited = analysis.get("citedSourceIds", [])
        if not isinstance(cited, list):
            cited = []
        analysis["citedSourceIds"] = [sid for sid in cited if str(sid) in allowed_source_ids]

        notes = analysis.get("citationNotes", [])
        if isinstance(notes, list):
            analysis["citationNotes"] = [
                note for note in notes if isinstance(note, dict) and str(note.get("sourceId") or "") in allowed_source_ids
            ]
        else:
            analysis["citationNotes"] = []

        applicable = analysis.get("applicableProvisionIds", [])
        if isinstance(applicable, list):
            analysis["applicableProvisionIds"] = [sid for sid in applicable if str(sid) in allowed_source_ids]
        else:
            analysis["applicableProvisionIds"] = []

    return {
        "query": query,
        "facts": facts,
        "provisions": provisions,
        "analysis": analysis,
        "analysisError": analysis_error,
        "analysisStatus": analysis_status,
        "analysisJobId": job_id,
        "grounding": {
            "strictSourceValidation": True,
            "allowedSourceIds": sorted([sid for sid in allowed_source_ids if sid]),
        },
        "retrievalDiagnostics": {
            "ragCount": rag_count,
            "webCount": web_count,
            "hybridCount": len(provisions),
            "seedCount": 0,
            "llmScoutCount": llm_scout_count,
            "webError": KNOWLEDGE_SERVICE.get_last_web_error() if KNOWLEDGE_SERVICE and hasattr(KNOWLEDGE_SERVICE, "get_last_web_error") else "",
            "pipeline": pipeline,
        },
    }


@app.get("/api/v1/knowledge-base/provision-lookup/analysis/{job_id}")
async def provision_lookup_analysis(job_id: str) -> Dict[str, Any]:
    with PROVISION_ANALYSIS_LOCK:
        if job_id in PROVISION_ANALYSIS_RESULTS:
            return {"jobId": job_id, "status": "ready", "analysis": PROVISION_ANALYSIS_RESULTS[job_id], "error": None}
        if job_id in PROVISION_ANALYSIS_TASKS:
            return {"jobId": job_id, "status": "pending", "analysis": None, "error": None}
        if job_id in PROVISION_ANALYSIS_ERRORS:
            return {"jobId": job_id, "status": "error", "analysis": None, "error": PROVISION_ANALYSIS_ERRORS[job_id]}
    return {"jobId": job_id, "status": "not_found", "analysis": None, "error": None}


@app.post("/api/v1/agents/issue-spotter")
async def issue_spotter(payload: GenericAgentRequest) -> List[GenericListItemResponse]:
    out = await llm_json("issue_spotter", payload.as_payload())
    return out.get("issues", []) if isinstance(out.get("issues", []), list) else []


@app.post("/api/v1/agents/case-finder")
async def case_finder(payload: GenericAgentRequest) -> List[GenericListItemResponse]:
    out = await llm_json("case_finder", payload.as_payload())
    return out.get("precedents", []) if isinstance(out.get("precedents", []), list) else []


@app.post("/api/v1/agents/limitation-checker")
async def limitation_checker(payload: GenericAgentRequest) -> GenericDictResponse:
    out = await llm_json("limitation_checker", payload.as_payload())
    return out.get("assessment", {}) if isinstance(out.get("assessment", {}), dict) else {}


@app.post("/api/v1/agents/argument-builder")
async def argument_builder(payload: GenericAgentRequest) -> GenericDictResponse:
    out = await llm_json("argument_builder", payload.as_payload())
    return out.get("argumentSet", {}) if isinstance(out.get("argumentSet", {}), dict) else {}


@app.post("/api/v1/agents/doc-composer")
async def doc_composer(payload: GenericAgentRequest) -> GenericDictResponse:
    out = await llm_json("doc_composer", payload.as_payload())
    return out.get("draft", {}) if isinstance(out.get("draft", {}), dict) else {}


@app.post("/api/v1/agents/compliance-guard")
async def compliance_guard(payload: GenericAgentRequest) -> List[GenericListItemResponse]:
    out = await llm_json("compliance_guard", payload.as_payload())
    return out.get("findings", []) if isinstance(out.get("findings", []), list) else []


@app.post("/api/v1/agents/aid-connector")
async def aid_connector(payload: GenericAgentRequest) -> GenericDictResponse:
    out = await llm_json("aid_connector", payload.as_payload())
    return out.get("aid", {}) if isinstance(out.get("aid", {}), dict) else {}


@app.post("/api/v1/agents/judgment-summarizer")
async def judgment_summarizer(file: UploadFile = File(...)) -> GenericDictResponse:
    judgment_text = await extract_text_from_upload(file)
    if len(judgment_text) < 120:
        raise HttpError(
            status=400,
            code="LOW_TEXT_CONTENT",
            message="Extracted judgment text is too short",
            user_message="Could not extract enough text from the file. Please upload a clearer judgment copy.",
        )

    out = await llm_json(
        "judgment_summarizer",
        {
            "fileName": file.filename or "judgment",
            "judgmentText": judgment_text[:50000],
            "instructions": "Summarize the judgment faithfully. If missing, return empty strings/arrays instead of guessing.",
        },
    )

    summary = out.get("summary", {}) if isinstance(out.get("summary", {}), dict) else {}
    summary["sourceFileName"] = file.filename or "judgment"
    return summary







































