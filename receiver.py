"""TCP receiver for the covert timing channel demo."""

from __future__ import annotations

import socket
import time
from dataclasses import dataclass

from analyzer import decode_relative_timings
from decoder import decode_binary_message
from visualizer import visualize


@dataclass(frozen=True)
class ReceiverConfig:
    host: str = "127.0.0.1"
    port: int = 5000
    key: str = "timing-key"
    tolerance: float = 0.01


def receive_timing_channel(config: ReceiverConfig) -> tuple[str, str]:
    """Receive one covert message and return the recovered bit stream and text."""

    arrival_times: list[float] = []

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((config.host, config.port))
        server.listen(1)
        print(f"[receiver] listening on {config.host}:{config.port}")

        connection, address = server.accept()
        with connection:
            print(f"[receiver] connection from {address[0]}:{address[1]}")
            connection_start = time.perf_counter()
            while True:
                chunk = connection.recv(1)
                if not chunk:
                    break

                arrival_time = time.perf_counter()
                arrival_times.append(arrival_time)
                print(
                    f"[receiver] packet {len(arrival_times):03d} arrived at {arrival_time:.6f}"
                )

    if not arrival_times:
        print("[receiver] no packets received")
        return "", ""

    arrival_delays = [arrival_times[0] - connection_start]
    arrival_delays.extend(
        arrival_times[index] - arrival_times[index - 1]
        for index in range(1, len(arrival_times))
    )

    analysis = decode_relative_timings(arrival_delays, tolerance=config.tolerance)
    masked_bits = analysis.bitstream
    recovered_text = decode_binary_message(masked_bits, config.key)

    print(f"[receiver] arrival delays: {['{:.4f}'.format(delay) for delay in analysis.arrival_delays]}")
    print(f"[receiver] delta values:    {['{:.4f}'.format(delta) for delta in analysis.deltas]}")
    print(f"[receiver] masked bits:     {masked_bits}")
    print(f"[receiver] decoded text:    {recovered_text}")
    visualize(analysis.arrival_delays, output_path="receiver_timing_plot.png", title="Receiver Arrival Delays")

    return masked_bits, recovered_text


def _prompt_text(label: str, default: str) -> str:
    value = input(f"{label} [{default}]: ").strip()
    return value or default


def _prompt_int(label: str, default: int) -> int:
    value = input(f"{label} [{default}]: ").strip()
    return int(value) if value else default


def _prompt_float(label: str, default: float) -> float:
    value = input(f"{label} [{default}]: ").strip()
    return float(value) if value else default


def prompt_config() -> ReceiverConfig:
    print("[receiver] enter values, or press Enter to accept defaults")
    return ReceiverConfig(
        host=_prompt_text("bind host", "127.0.0.1"),
        port=_prompt_int("listen port", 5000),
        key=_prompt_text("masking key", "timing-key"),
        tolerance=_prompt_float("timing tolerance", 0.01),
    )


def main() -> None:
    config = prompt_config()
    receive_timing_channel(config)


if __name__ == "__main__":
    main()