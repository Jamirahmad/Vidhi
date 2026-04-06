import json
import logging

from backend.app.logging_config import JsonFormatter, configure_logging, get_logger, log_event


def test_json_formatter_includes_structured_fields() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="vidhi.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="event",
        args=(),
        exc_info=None,
    )
    record.structured_fields = {"request_id": "abc", "status": 200}

    parsed = json.loads(formatter.format(record))

    assert parsed["logger"] == "vidhi.test"
    assert parsed["message"] == "event"
    assert parsed["request_id"] == "abc"
    assert parsed["status"] == 200


def test_configure_logging_and_log_event() -> None:
    configure_logging()
    logger = get_logger("vidhi.test")

    log_event(logger, logging.WARNING, "warning_event", code="TEST", status=400)

    assert logger.name == "vidhi.test"
