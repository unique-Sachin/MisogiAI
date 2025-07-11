"""Celery application initialization.

Uses Redis as both broker and result backend (development default).
"""
from __future__ import annotations

import os

from celery import Celery  # type: ignore

REDIS_URL = os.getenv("REDIS_BROKER_URL", "redis://localhost:6379/0")
CELERY_QUEUE = os.getenv("CELERY_QUEUE", "financial_rag")

celery_app = Celery(
    "financial_rag",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_default_queue=CELERY_QUEUE,
) 