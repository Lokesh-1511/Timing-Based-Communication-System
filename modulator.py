"""Relative timing generation for the covert timing channel demo.

The first generated delay acts as a reference. Each subsequent delay encodes a
bit as an increase or decrease relative to the previous delay.
"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class TimingConfig:
    base_delay: float = 0.2
    step: float = 0.05
    jitter: float = 0.01
    min_delay: float = 0.1
    max_delay: float = 0.4


@dataclass(frozen=True)
class TimingPlan:
    bits: str
    delays: list[float]
    config: TimingConfig


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _validate_bits(bits: str) -> None:
    if any(bit not in {"0", "1"} for bit in bits):
        raise ValueError("bits must contain only '0' and '1'")


def bits_to_relative_delays(
    bits: str,
    *,
    base_delay: float = 0.2,
    step: float = 0.05,
    jitter: float = 0.01,
    min_delay: float = 0.1,
    max_delay: float = 0.4,
    seed: int | None = None,
) -> list[float]:
    """Convert bits into a relative timing sequence.

    The returned list includes one reference delay followed by one delay per
    bit. A '1' increases the delay from the previous step; a '0' decreases it.
    Small random jitter is added to every step to reduce obvious patterns.
    """

    _validate_bits(bits)
    config = TimingConfig(base_delay, step, jitter, min_delay, max_delay)
    rng = Random(seed)

    current_delay = _clamp(
        config.base_delay + rng.uniform(-config.jitter, config.jitter),
        config.min_delay,
        config.max_delay,
    )
    delays = [current_delay]

    for bit in bits:
        direction = 1.0 if bit == "1" else -1.0
        noisy_step = direction * config.step + rng.uniform(-config.jitter, config.jitter)
        current_delay = _clamp(current_delay + noisy_step, config.min_delay, config.max_delay)
        delays.append(current_delay)

    return delays


def build_timing_plan(
    bits: str,
    *,
    base_delay: float = 0.2,
    step: float = 0.05,
    jitter: float = 0.01,
    min_delay: float = 0.1,
    max_delay: float = 0.4,
    seed: int | None = None,
) -> TimingPlan:
    """Build a timing plan that is easy to inspect in tests."""

    config = TimingConfig(base_delay, step, jitter, min_delay, max_delay)
    delays = bits_to_relative_delays(
        bits,
        base_delay=base_delay,
        step=step,
        jitter=jitter,
        min_delay=min_delay,
        max_delay=max_delay,
        seed=seed,
    )
    return TimingPlan(bits=bits, delays=delays, config=config)


__all__ = [
    "TimingConfig",
    "TimingPlan",
    "bits_to_relative_delays",
    "build_timing_plan",
]