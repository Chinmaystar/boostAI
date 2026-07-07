from __future__ import annotations

import random
from typing import Any, Protocol

from src.variable_engine import VariableDomain, VariableType


class SamplingStrategy(Protocol):
    def sample(self, domain: VariableDomain, var_type: VariableType) -> Any:
        ...


class UniformSampler:
    def __init__(self, rng: random.Random) -> None:
        self._rng = rng

    def sample(self, domain: VariableDomain, var_type: VariableType) -> Any:
        if domain.allowed_values:
            return self._rng.choice(list(domain.allowed_values))

        if var_type == VariableType.INTEGER:
            return self._sample_int(domain)
        if var_type == VariableType.DECIMAL:
            return self._sample_float(domain)
        if var_type == VariableType.COORDINATE:
            return self._sample_coordinate(domain)
        if var_type == VariableType.PROBABILITY:
            return self._sample_probability(domain)
        if var_type == VariableType.PERCENTAGE:
            return self._sample_percentage(domain)
        if var_type in (VariableType.LENGTH, VariableType.RADIUS,
                        VariableType.DIAMETER, VariableType.AREA,
                        VariableType.VOLUME):
            return self._sample_positive_float(domain)
        if var_type in (VariableType.ANGLE,):
            return self._sample_angle(domain)
        if var_type in (VariableType.POINT,):
            return self._sample_point(domain)

        return self._sample_int(domain)

    def _sample_int(self, domain: VariableDomain) -> int:
        lo, hi = self._int_bounds(domain)
        return self._rng.randint(lo, hi)

    def _sample_float(self, domain: VariableDomain) -> float:
        lo, hi = self._float_bounds(domain)
        val = self._rng.uniform(lo, hi)
        return round(val, 2)

    def _sample_coordinate(self, domain: VariableDomain) -> tuple[float, float]:
        lo, hi = self._float_bounds(domain)
        x = round(self._rng.uniform(lo, hi), 2)
        y = round(self._rng.uniform(lo, hi), 2)
        return (x, y)

    def _sample_point(self, domain: VariableDomain) -> tuple[float, float]:
        return self._sample_coordinate(domain)

    def _sample_probability(self, domain: VariableDomain) -> float:
        lo = max(0.0, domain.min_value or 0.0)
        hi = min(1.0, domain.max_value or 1.0)
        val = self._rng.uniform(lo, hi)
        return round(val, 4)

    def _sample_percentage(self, domain: VariableDomain) -> float:
        lo = max(0.0, domain.min_value or 0.0)
        hi = min(100.0, domain.max_value or 100.0)
        val = self._rng.uniform(lo, hi)
        return round(val, 2)

    def _sample_positive_float(self, domain: VariableDomain) -> float:
        lo = max(0.1, domain.min_value or 0.1)
        hi = domain.max_value or 100.0
        val = self._rng.uniform(lo, hi)
        return round(val, 2)

    def _sample_angle(self, domain: VariableDomain) -> float:
        lo = max(0.0, domain.min_value or 0.0)
        hi = min(360.0, domain.max_value or 360.0)
        val = self._rng.uniform(lo, hi)
        return round(val, 1)

    def _int_bounds(self, domain: VariableDomain) -> tuple[int, int]:
        lo = int(domain.min_value) if domain.min_value is not None else 1
        hi = int(domain.max_value) if domain.max_value is not None else 20
        if domain.is_positive:
            lo = max(1, lo)
        if domain.is_negative:
            lo = int(domain.min_value) if domain.min_value is not None else -20
            hi = min(-1, hi if domain.max_value is not None else -1)
        if lo > hi:
            lo, hi = hi, lo
        return lo, hi

    def _float_bounds(self, domain: VariableDomain) -> tuple[float, float]:
        lo = domain.min_value if domain.min_value is not None else -10.0
        hi = domain.max_value if domain.max_value is not None else 10.0
        if domain.is_positive:
            lo = max(0.1, lo)
        if domain.is_negative:
            lo = domain.min_value if domain.min_value is not None else -20.0
            hi = min(-0.1, hi if domain.max_value is not None else -0.1)
        if lo > hi:
            lo, hi = hi, lo
        return lo, hi


class DomainSampler:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._strategies: dict[str, SamplingStrategy] = {
            "uniform": UniformSampler(self._rng),
        }

    def register_strategy(self, name: str, strategy: SamplingStrategy) -> None:
        self._strategies[name] = strategy

    def sample(
        self,
        domain: VariableDomain,
        var_type: VariableType,
        strategy: str = "uniform",
    ) -> Any:
        s = self._strategies.get(strategy)
        if s is None:
            s = self._strategies["uniform"]
        return s.sample(domain, var_type)

    def reseed(self, seed: int) -> None:
        self._rng.seed(seed)
