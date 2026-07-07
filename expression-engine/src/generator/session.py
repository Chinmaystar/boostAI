from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from src.constraint_engine import RetryReason

from .question import GenerationStats


@dataclass
class GeneratorSession:
    template_id: str
    max_retries: int

    _start_time: float = field(default_factory=time.time)
    _attempts: int = 0
    _retries: int = 0
    _validation_calls: int = 0
    _constraint_failures: dict[str, int] = field(default_factory=dict)
    _retry_reasons: list[RetryReason] = field(default_factory=list)
    _success: bool = False

    def record_attempt(self) -> None:
        self._attempts += 1

    def record_retry(self, reason: RetryReason) -> None:
        self._retries += 1
        self._retry_reasons.append(reason)

    def record_validation_call(self) -> None:
        self._validation_calls += 1

    def record_constraint_failure(self, constraint_id: str) -> None:
        self._constraint_failures[constraint_id] = (
            self._constraint_failures.get(constraint_id, 0) + 1
        )

    def mark_success(self) -> None:
        self._success = True

    @property
    def attempts(self) -> int:
        return self._attempts

    @property
    def retries(self) -> int:
        return self._retries

    @property
    def elapsed_ms(self) -> float:
        return (time.time() - self._start_time) * 1000.0

    @property
    def can_retry(self) -> bool:
        return self._retries < self.max_retries and not self._success

    def to_stats(self) -> GenerationStats:
        return GenerationStats(
            attempts=self._attempts,
            retries=self._retries,
            total_time_ms=self.elapsed_ms,
            validation_calls=self._validation_calls,
            constraint_failures=dict(self._constraint_failures),
            success=self._success,
        )

    def last_retry_reason(self) -> RetryReason | None:
        if self._retry_reasons:
            return self._retry_reasons[-1]
        return None
