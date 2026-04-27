"""TCP sender for the covert timing channel demo.

This client sends a single sync packet followed by timed packets whose spacing
encodes the masked bit stream.
"""

from __future__ import annotations

import socket
import time
from dataclasses import dataclass

from encoder import EncodedMessage, encode_text
from modulator import TimingPlan, build_timing_plan
from visualizer import visualize


@dataclass(frozen=True)
class SenderConfig:
    host: str = "127.0.0.1"
    port: int = 5000
    key: str = "timing-key"
    text: str = "hello"
    base_delay: float = 0.2
    step: float = 0.05
    jitter: float = 0.01
    min_delay: float = 0.1
    max_delay: float = 0.4
    seed: int | None = None


def estimate_timing_values(bit_count: int) -> tuple[float, float, float, float, float]:
    """Pick practical timing defaults based on payload size."""

    base_delay = 0.2
    if bit_count <= 64:
        step = 0.05
    elif bit_count <= 256:
        step = 0.04
    else:
        step = 0.03

    jitter = max(0.004, min(0.012, step * 0.2))
    min_delay = max(0.06, base_delay - step - jitter)
    max_delay = min(0.5, base_delay + step + jitter + 0.15)
    return base_delay, step, jitter, min_delay, max_delay


def build_sender_plan(config: SenderConfig) -> tuple[EncodedMessage, TimingPlan]:
    encoded = encode_text(config.text, config.key)
    timing_plan = build_timing_plan(
        encoded.masked_bits,
        base_delay=config.base_delay,
        step=config.step,
        jitter=config.jitter,
        min_delay=config.min_delay,
        max_delay=config.max_delay,
        seed=config.seed,
    )
    return encoded, timing_plan


def send_timing_channel(config: SenderConfig) -> None:
    encoded, timing_plan = build_sender_plan(config)

    print(f"[sender] text: {encoded.text}")
    print(f"[sender] plain bits:  {encoded.plain_bits}")
    print(f"[sender] masked bits: {encoded.masked_bits}")
    print(f"[sender] delays:      {['{:.4f}'.format(delay) for delay in timing_plan.delays]}")
    visualize(timing_plan.delays, output_path="sender_timing_plot.png", title="Sender Timing Plan")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        client.connect((config.host, config.port))

        # Reference packet so the receiver can measure relative changes from a baseline.
        time.sleep(timing_plan.delays[0])
        client.sendall(b"S")
        print(f"[sender] sent sync packet at {time.perf_counter():.6f}")

        for index, delay in enumerate(timing_plan.delays[1:], start=0):
            time.sleep(delay)
            client.sendall(b"D")
            print(
                f"[sender] sent data packet {index:03d} after delay {delay:.4f}s at {time.perf_counter():.6f}"
            )


def _prompt_text(label: str, default: str) -> str:
    value = input(f"{label} [{default}]: ").strip()
    return value or default


def prompt_config() -> SenderConfig:
    print("[sender] enter message settings, timing is auto-selected")
    text = _prompt_text("text to send", "hello")
    key = _prompt_text("masking key", "timing-key")
    bit_count = len(encode_text(text, key).masked_bits)
    base_delay, step, jitter, min_delay, max_delay = estimate_timing_values(bit_count)

    print(
        "[sender] auto timing: "
        f"base={base_delay:.3f}s step={step:.3f}s jitter={jitter:.3f}s "
        f"min={min_delay:.3f}s max={max_delay:.3f}s"
    )

    return SenderConfig(
        key=key,
        text=text,
        base_delay=base_delay,
        step=step,
        jitter=jitter,
        min_delay=min_delay,
        max_delay=max_delay,
        seed=None,
    )


def main() -> None:
    config = prompt_config()
    send_timing_channel(config)


if __name__ == "__main__":
    main()