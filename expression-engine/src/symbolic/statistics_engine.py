from __future__ import annotations

import math
from typing import Optional

from .backend import SymbolicBackend
from .exceptions import DomainError, RangeError


class FrequencyTable:
    """A frequency table for a data set."""

    def __init__(self, data: list[float]) -> None:
        self._freq: dict[float, int] = {}
        for v in data:
            self._freq[v] = self._freq.get(v, 0) + 1
        self._total = len(data)

    @property
    def frequencies(self) -> dict[float, int]:
        return dict(self._freq)

    @property
    def total(self) -> int:
        return self._total

    def relative_frequency(self, value: float) -> float:
        if self._total == 0:
            return 0.0
        return self._freq.get(value, 0) / self._total

    def cumulative_frequency(self, value: float) -> int:
        return sum(v for k, v in self._freq.items() if k <= value)

    def modal_values(self) -> list[float]:
        if not self._freq:
            return []
        max_freq = max(self._freq.values())
        return sorted(k for k, v in self._freq.items() if v == max_freq)


class GroupedFrequencyTable:
    """A grouped frequency table."""

    def __init__(self, intervals: list[tuple[float, float]],
                 data: list[float]) -> None:
        self._intervals = list(intervals)
        self._freq: dict[int, int] = {}
        for v in data:
            for i, (lo, hi) in enumerate(intervals):
                if lo <= v < hi:
                    self._freq[i] = self._freq.get(i, 0) + 1
                    break
        self._total = len(data)

    @property
    def intervals(self) -> list[tuple[float, float]]:
        return list(self._intervals)

    @property
    def frequencies(self) -> dict[int, int]:
        return dict(self._freq)

    @property
    def total(self) -> int:
        return self._total

    def interval_frequency(self, lo: float, hi: float) -> int:
        for i, (ilo, ihi) in enumerate(self._intervals):
            if abs(ilo - lo) < 1e-12 and abs(ihi - hi) < 1e-12:
                return self._freq.get(i, 0)
        return 0


class StatisticsEngine:
    """Statistics calculations.

    Provides mean, median, mode, range, frequency tables, grouped
    frequency, probability, and percentage computations.
    """

    def __init__(self, backend: SymbolicBackend) -> None:
        self._backend = backend

    @property
    def backend(self) -> SymbolicBackend:
        return self._backend

    # ── descriptive statistics ─────────────────────────────────

    def mean(self, data: list[float]) -> float:
        if not data:
            raise ValueError("Cannot compute mean of empty list")
        return self._backend.mean(data)

    def median(self, data: list[float]) -> float:
        if not data:
            raise ValueError("Cannot compute median of empty list")
        return self._backend.median(data)

    def mode(self, data: list[float]) -> list[float]:
        if not data:
            raise ValueError("Cannot compute mode of empty list")
        return self._backend.mode(data)

    def data_range(self, data: list[float]) -> float:
        if not data:
            raise ValueError("Cannot compute range of empty list")
        return self._backend.data_range(data)

    def min(self, data: list[float]) -> float:
        if not data:
            raise ValueError("Cannot compute min of empty list")
        return min(data)

    def max(self, data: list[float]) -> float:
        if not data:
            raise ValueError("Cannot compute max of empty list")
        return max(data)

    # ── frequency ──────────────────────────────────────────────

    def frequency(self, data: list[float]) -> dict[float, int]:
        return self._backend.frequency(data)

    def frequency_table(self, data: list[float]) -> FrequencyTable:
        return FrequencyTable(data)

    def grouped_frequency(self, data: list[float],
                          intervals: list[tuple[float, float]]
                          ) -> GroupedFrequencyTable:
        return GroupedFrequencyTable(intervals, data)

    # ── probability & percentage ───────────────────────────────

    def probability(self, favorable: int, total: int) -> float:
        return self._backend.probability(favorable, total)

    def percentage(self, value: float, total: float) -> float:
        return self._backend.percentage(value, total)

    # ── variance & standard deviation ──────────────────────────

    def variance(self, data: list[float], population: bool = True
                 ) -> float:
        if not data:
            raise ValueError("Cannot compute variance of empty list")
        m = self.mean(data)
        n = len(data)
        divisor = n if population else n - 1
        if divisor == 0:
            raise ValueError(
                "Sample variance requires at least 2 data points")
        return sum((v - m) ** 2 for v in data) / divisor

    def std_dev(self, data: list[float], population: bool = True
                ) -> float:
        return math.sqrt(self.variance(data, population))
