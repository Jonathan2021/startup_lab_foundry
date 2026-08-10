"""Application logging configuration."""

from __future__ import annotations

import logging
import sys
from contextvars import ContextVar

correlation_id_var: ContextVar[str] = ContextVar(
    "correlation_id",
    default="-",
)

class CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_var.get()
        return True

def configure_logging(*, debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO

    handler = logging.StreamHandler(sys.stderr)
    handler.addFilter(CorrelationIdFilter())

    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s "
            "correlation_id=%(correlation_id)s %(message)s"
        )
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)