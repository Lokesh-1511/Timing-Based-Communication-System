"""Visualization helpers for covert timing channel experiments.

This module is optional. It will plot timing data when matplotlib is available
and still provide a useful textual summary otherwise.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TimingSeries:
    labels: list[str]
    delays: list[float]


def summarize_timing(delays: list[float]) -> str:
    if not delays:
        return "no timing data"

    minimum = min(delays)
    maximum = max(delays)
    average = sum(delays) / len(delays)
    return f"count={len(delays)} min={minimum:.4f}s max={maximum:.4f}s avg={average:.4f}s"


def plot_timing(delays: list[float], *, output_path: str | None = None, title: str = "Timing Channel") -> str:
    """Plot timing data if matplotlib is installed.

    Returns the output path for convenience. If no output path is provided, a
    PNG named `timing_plot.png` is created in the current working directory.
    """

    if not delays:
        raise ValueError("delays must not be empty")

    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - exercised manually when missing
        raise RuntimeError("matplotlib is required for plotting") from exc

    resolved_path = Path(output_path or "timing_plot.png")
    x_values = list(range(len(delays)))

    figure, axis = plt.subplots(figsize=(10, 4))
    axis.plot(x_values, delays, marker="o", linewidth=2)
    axis.set_title(title)
    axis.set_xlabel("Packet index")
    axis.set_ylabel("Delay (s)")
    axis.grid(True, alpha=0.3)
    figure.tight_layout()
    figure.savefig(resolved_path, dpi=150)
    plt.close(figure)

    return str(resolved_path)


def visualize(delays: list[float], *, output_path: str | None = None, title: str = "Timing Channel") -> None:
    """Print a compact summary and plot the timing data when possible."""

    print(f"[visualizer] {summarize_timing(delays)}")
    try:
        path = plot_timing(delays, output_path=output_path, title=title)
        print(f"[visualizer] wrote plot to {path}")
    except RuntimeError as exc:
        print(f"[visualizer] plotting skipped: {exc}")


def _prompt_text(label: str, default: str) -> str:
    value = input(f"{label} [{default}]: ").strip()
    return value or default


def _prompt_delays() -> list[float]:
    raw_value = input("delay values separated by spaces [blank for none]: ").strip()
    if not raw_value:
        return []
    return [float(part) for part in raw_value.split()]


def prompt_config() -> tuple[list[float], str | None, str]:
    print("[visualizer] enter values, or press Enter to accept defaults")
    delays = _prompt_delays()
    output_path = _prompt_text("output image path", "timing_plot.png")
    title = _prompt_text("plot title", "Timing Channel")
    return delays, output_path, title


def main() -> None:
    delays, output_path, title = prompt_config()
    visualize(delays, output_path=output_path, title=title)


if __name__ == "__main__":
    main()