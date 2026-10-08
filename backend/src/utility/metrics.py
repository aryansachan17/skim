from prometheus_client import Histogram

REQUEST_LATENCY = Histogram(
    "skim_http_request_duration_seconds",
    "Time taken to handle an HTTP request",
    ["method", "route", "status"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
