from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.error_handlers import HttpError, http_error_payload, install_exception_handlers
from backend.app.logging_config import configure_logging, get_logger


def test_http_error_payload_shape() -> None:
    err = HttpError(status=400, code="BAD_INPUT", message="Bad input", user_message="Please fix")

    payload = http_error_payload(err)

    assert payload == {
        "error": "Bad input",
        "code": "BAD_INPUT",
        "userMessage": "Please fix",
    }


def test_installed_exception_handlers_return_normalized_responses() -> None:
    app = FastAPI()
    configure_logging()
    app.state.request_logger = get_logger("vidhi.test")
    install_exception_handlers(app)

    @app.get("/http-error")
    async def _http_error() -> dict:
        raise HttpError(status=418, code="TEAPOT", message="I am teapot", user_message="Try again")

    @app.get("/boom")
    async def _boom() -> dict:
        raise RuntimeError("boom")

    client = TestClient(app, raise_server_exceptions=False)

    http_resp = client.get("/http-error")
    assert http_resp.status_code == 418
    assert http_resp.json()["code"] == "TEAPOT"

    generic_resp = client.get("/boom")
    assert generic_resp.status_code == 500
    assert generic_resp.json()["code"] == "INTERNAL_ERROR"
