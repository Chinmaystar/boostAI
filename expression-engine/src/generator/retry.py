from __future__ import annotations

from src.constraint_engine import ConstraintValidationResult

from .config import GeneratorConfig
from .errors import NoValidAssignmentError
from .session import GeneratorSession


class RetryManager:
    def __init__(self, config: GeneratorConfig) -> None:
        self._config = config

    def should_retry(
        self,
        session: GeneratorSession,
        result: ConstraintValidationResult,
    ) -> bool:
        if result.valid:
            return False
        if not session.can_retry:
            return False
        return True

    def get_backoff_ms(self, retry_count: int) -> float:
        return self._config.retry_backoff_base_ms * (retry_count + 1)

    def raise_if_exhausted(self, session: GeneratorSession) -> None:
        if session.can_retry:
            return
        reason = session.last_retry_reason()
        reason_str = reason.value if reason else "unknown"
        raise NoValidAssignmentError(
            f"Failed to generate valid assignment after "
            f"{session.attempts} attempt(s). "
            f"Last retry reason: {reason_str}"
        )



