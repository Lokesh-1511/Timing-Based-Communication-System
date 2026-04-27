"""Timing analysis helpers for recovering bits from packet arrivals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class TimingAnalysis:
    """Human-readable result of decoding relative timing differences."""

    arrival_delays: list[float]
    bitstream: str
    deltas: list[float]


def _classify_delta(delta: float, tolerance: float, previous_bit: str) -> str:
    if delta > tolerance:
        return "1"
    if delta < -tolerance:
        return "0"
    return previous_bit


def decode_relative_timings(
    arrival_delays: Sequence[float],
    *,
    tolerance: float = 0.01,
) -> TimingAnalysis:
    """Decode bits by comparing consecutive delay changes.

    The first delay acts as the reference baseline. Each later delay is
    compared to the previous one; an increase maps to '1' and a decrease maps
    to '0'. Small fluctuations inside the tolerance window reuse the previous
    decision to avoid overreacting to jitter.
    """

    if len(arrival_delays) < 2:
        return TimingAnalysis(arrival_delays=list(arrival_delays), bitstream="", deltas=[])

    bitstream: list[str] = []
    deltas: list[float] = []
    previous_delay = arrival_delays[0]
    previous_bit = "1" if arrival_delays[1] >= arrival_delays[0] else "0"

    for current_delay in arrival_delays[1:]:
        delta = current_delay - previous_delay
        bit = _classify_delta(delta, tolerance, previous_bit)
        bitstream.append(bit)
        deltas.append(delta)
        previous_delay = current_delay
        previous_bit = bit

    return TimingAnalysis(
        arrival_delays=list(arrival_delays),
        bitstream="".join(bitstream),
        deltas=deltas,
    )


__all__ = ["TimingAnalysis", "decode_relative_timings"]