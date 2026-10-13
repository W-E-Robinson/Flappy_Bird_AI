"""Graphs for inspecting recorded scores.

Each graph function reads one of the files written by the other scripts and
saves a timestamped PNG to ./src/__graphs__/ (relative to where the script is
run from), so graphs from separate sessions sit side by side.
"""

import os
from datetime import datetime
from statistics import median
from constants import GRAPH_MODE
import matplotlib

matplotlib.use("Agg")  # Save to file, no GUI backend needed
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator

GRAPHS_DIR = "./src/__graphs__"
SCORES_FILE = "./src/scores_last_test_session.txt"
TEST_RUN_SCORES_FILE = "./src/scores_last_test_run.txt"

# Chart palette - validated light mode steps, mark colour carries the series,
# all text stays in ink colours
SURFACE = "#fcfcfb"
PRIMARY_INK = "#0b0b0b"
SECONDARY_INK = "#52514e"
MUTED_INK = "#898781"
GRIDLINE = "#e1e0d9"
AXIS_LINE = "#c3c2b7"
SERIES_COLOUR = "#2a78d6"  # The rolling mean - the line the eye should follow
CONTEXT_COLOUR = "#898781"  # Per episode noise, deliberately recessive

FONT_FAMILY = ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]
FIGURE_SIZE_INCHES = (10.0, 5.0)
FIGURE_DPI = 200
# Smooth over this fraction of the session, so the window scales with its length
ROLLING_WINDOW_FRACTION = 50


def load_scores(file_path: str) -> list[int]:
    """Reads one score per line, ignoring the trailing blank line."""
    with open(file_path, "r") as f:
        lines = f.read().splitlines()
    return [int(line) for line in lines if line.strip()]


def rolling_mean(scores: list[int], window: int) -> list[float]:
    """Mean of the last `window` scores, over a shrinking window at the start."""
    means = []
    running_total = 0
    for idx, score in enumerate(scores):
        running_total += score
        if idx >= window:
            running_total -= scores[idx - window]
        means.append(running_total / min(idx + 1, window))
    return means


def style_axes(ax, title: str, subtitle: str, x_label: str, y_label: str) -> None:
    """Recessive chrome: hairline y gridlines, muted ticks, no top/right spines."""
    ax.set_facecolor(SURFACE)
    ax.set_title(title, color=PRIMARY_INK, fontsize=13, loc="left", pad=22)
    ax.text(
        0.0,
        1.02,
        subtitle,
        transform=ax.transAxes,
        color=SECONDARY_INK,
        fontsize=9.5,
    )
    ax.set_xlabel(x_label, color=SECONDARY_INK, fontsize=10, labelpad=8)
    ax.set_ylabel(y_label, color=SECONDARY_INK, fontsize=10, labelpad=8)

    ax.grid(axis="y", color=GRIDLINE, linewidth=1, linestyle="-")
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS_LINE)
        ax.spines[side].set_linewidth(1)
    ax.tick_params(colors=MUTED_INK, labelsize=9, length=0)


def timestamped_path(name: str) -> str:
    """./src/__graphs__/<timestamp>-<name>.png, matching the model file naming."""
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    return f"{GRAPHS_DIR}/{timestamp}-{name}.png"


def save_figure(fig, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(
        output_path,
        dpi=FIGURE_DPI,
        facecolor=SURFACE,
        bbox_inches="tight",
        # Drop the Software tag matplotlib writes by default, so the only
        # thing in the file is the chart
        metadata={"Software": None},
    )
    plt.close(fig)
    return output_path


def graph_scores_last_test_session(
    file_path: str = SCORES_FILE,
    output_path: str | None = None,
    window: int | None = None,
) -> str:
    """Score per episode for the last session, with the trend on top.

    The per episode scores are the context and the rolling mean is the point,
    so the raw line is greyed back and only the mean carries a colour.
    """
    if output_path is None:
        output_path = timestamped_path("scores_last_test_session")

    scores = load_scores(file_path)
    if not scores:
        raise ValueError(f"No scores found in {file_path}")

    if window is None:
        window = max(1, len(scores) // ROLLING_WINDOW_FRACTION)
    means = rolling_mean(scores, window)
    episodes = range(1, len(scores) + 1)

    plt.rcParams["font.family"] = FONT_FAMILY
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_INCHES)
    fig.patch.set_facecolor(SURFACE)

    ax.plot(
        episodes,
        scores,
        color=CONTEXT_COLOUR,
        linewidth=0.5,
        alpha=0.22,
        label="Score per episode",
        zorder=2,
    )
    ax.plot(
        episodes,
        means,
        color=SERIES_COLOUR,
        linewidth=2,
        solid_joinstyle="round",
        solid_capstyle="round",
        label=f"Rolling mean ({window} episodes)",
        zorder=3,
    )
    # End dot, ringed in the surface colour so it stays legible over the lines
    ax.plot(
        len(scores),
        means[-1],
        marker="o",
        markersize=7,
        color=SERIES_COLOUR,
        markeredgecolor=SURFACE,
        markeredgewidth=2,
        zorder=4,
    )

    style_axes(
        ax,
        title="Score per episode, last session",
        subtitle=f"{len(scores):,} episodes · best {max(scores):,} · mean {sum(scores) / len(scores):.2f}",
        x_label="Episode",
        y_label="Score (gaps cleared)",
    )
    ax.set_xlim(1, len(scores))
    # Scores are whole gaps cleared, so keep the axis on whole numbers even
    # when nothing was ever scored
    ax.set_ylim(0, max(1, max(scores)) * 1.05)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _pos: f"{value:,.0f}"))

    # Label the end of the trend only - the axis carries the rest
    ax.annotate(
        f"{means[-1]:.2f}",
        xy=(len(scores), means[-1]),
        xytext=(8, 0),
        textcoords="offset points",
        color=SECONDARY_INK,
        fontsize=9.5,
        va="center",
    )

    legend = ax.legend(
        frameon=False,
        loc="upper left",
        fontsize=9.5,
        handlelength=1.6,
        borderpad=0.0,
    )
    for text in legend.get_texts():
        text.set_color(SECONDARY_INK)

    return save_figure(fig, output_path)


def graph_scores_last_test_run(
    file_path: str = TEST_RUN_SCORES_FILE,
    output_path: str | None = None,
) -> str:
    if output_path is None:
        output_path = timestamped_path("scores_last_test_run")

    scores = load_scores(file_path)
    if not scores:
        raise ValueError(f"No scores found in {file_path}")

    lowest, highest = min(scores), max(scores)
    bin_width = max(1, -(-(highest - lowest + 1) // 40))
    edges = range(lowest, highest + bin_width + 1, bin_width)
    counts = [0] * (len(list(edges)) - 1)
    for score in scores:
        counts[min((score - lowest) // bin_width, len(counts) - 1)] += 1
    starts = [lowest + idx * bin_width for idx in range(len(counts))]

    middle = median(scores)

    plt.rcParams["font.family"] = FONT_FAMILY
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_INCHES)
    fig.patch.set_facecolor(SURFACE)

    ax.bar(
        starts,
        counts,
        width=bin_width * 0.88,
        align="edge",
        color=SERIES_COLOUR,
        linewidth=0,
        zorder=3,
    )
    ax.axvline(middle, color=PRIMARY_INK, linewidth=1.5, linestyle="--", zorder=4)
    ax.annotate(
        f"median {middle:.0f}",
        xy=(middle, max(counts)),
        xytext=(6, -2),
        textcoords="offset points",
        color=PRIMARY_INK,
        fontsize=9.5,
        va="top",
    )
    ax.axvline(highest, color=MUTED_INK, linewidth=1, linestyle="--", zorder=4)
    ax.annotate(
        f"max {highest:,}",
        xy=(highest, max(counts)),
        xytext=(-6, -2),
        textcoords="offset points",
        color=SECONDARY_INK,
        fontsize=9.5,
        ha="right",
        va="top",
    )

    style_axes(
        ax,
        title="Score distribution, last test run",
        subtitle=(
            f"{len(scores):,} seeded courses · median {middle:.0f} · "
            f"mean {sum(scores) / len(scores):.2f} · best {highest:,}"
        ),
        x_label="Score (gaps cleared)",
        y_label="Courses",
    )
    ax.set_xlim(lowest - bin_width, highest + bin_width * 2)
    ax.set_ylim(0, max(counts) * 1.12)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    return save_figure(fig, output_path)


GRAPH_PER_MODE = {
    "SESSION": graph_scores_last_test_session,
    "TEST_RUN": graph_scores_last_test_run,
}


def main():
    output_path = GRAPH_PER_MODE[GRAPH_MODE]()
    print(f"Saved graph to: {output_path}")


if __name__ == "__main__":
    main()
