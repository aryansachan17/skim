import json
import logging

from app.g import request_id_var
from logger import JsonFormatter, RequestContextFilter


def test_log_lines_are_json_and_carry_the_request_id():
    token = request_id_var.set("req-123")
    record = logging.LogRecord("skim", logging.INFO, __file__, 1, "hello", None, None)
    RequestContextFilter().filter(record)
    request_id_var.reset(token)

    line = json.loads(JsonFormatter().format(record))

    assert line["msg"] == "hello"
    assert line["request_id"] == "req-123"


def test_metrics_record_request_latency_by_route(client):
    client.get("/healthCheck")

    body = client.get("/metrics").text

    assert 'skim_http_request_duration_seconds_count{method="GET",route="/healthCheck"' in body
