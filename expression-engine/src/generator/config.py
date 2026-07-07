from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class GeneratorConfig:
    max_retries: int = 10
    random_seed: int | None = None
    sampling_strategy: str = "uniform"
    difficulty_overrides: dict[str, str] | None = None
    plugin_config: dict[str, Any] | None = None
    timeout_ms: int = 5000
    require_validation: bool = True
    retry_backoff_base_ms: float = 10.0
