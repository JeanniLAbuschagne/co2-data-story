"""
Task 2 - Improving a Data Visualization by Telling a Data Story
Data: Our World in Data, CO2 emissions per capita (https://github.com/owid/co2-data)

Produces four figures in ./figures/:
  fig0_baseline.png      - default matplotlib line chart (deliberately sub-optimal)
  fig1_highlight_line.png - focused line chart with highlighted countries
  fig2_slope.png          - slope chart, first vs last year
  fig3_ranked_bar.png     - ranked horizontal bar chart with world average

Run:  pip install pandas matplotlib
      python task2_charts.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# --------------------------------------------------------------------------
# Settings you can change
# --------------------------------------------------------------------------
# Pinned to the dataset version of 2 June 2026 (commit 382ee6c) so the figures
# can be reproduced exactly; use ".../co2-data/master/..." for the newest data.
DATA_URL = ("https://raw.githubusercontent.com/owid/co2-data/"
            "382ee6c662b0ece26e111f263b44c029afad7787/owid-co2-data.csv")
LOCAL_FILE = Path("owid-co2-data.csv")
OUT_DIR = Path("figures")

START_YEAR = 1990

COUNTRIES = [
    "United States", "Australia", "Canada", "Saudi Arabia", "Russia",
    "Germany", "Japan", "South Korea", "China", "United Kingdom",
    "France", "Italy", "Spain", "Poland", "South Africa", "Iran",
    "Mexico", "Brazil", "Turkey", "Indonesia", "India", "Nigeria",
]

# Countries that carry the story in figures 1 and 2 (each gets its own colour)
HIGHLIGHT = {
    "United States": "#1f5fa8",
    "United Kingdom": "#2a9d8f",
    "China": "#d1495b",
    "India": "#e8a33d",
}

# Typeface for the three improved charts (the baseline keeps all defaults).
# Liberation Sans is a metric-compatible fallback where Arial is not installed.
IMPROVED_RC = {"font.family": "sans-serif",
               "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"]}

GREY = "#c4c4c4"
DARK = "#333333"
UP = "#d1495b"     # emissions rose
DOWN = "#1f5fa8"   # emissions fell


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
def load_data() -> pd.DataFrame:
    if not LOCAL_FILE.exists():
        print("Downloading OWID CO2 data ...")
        pd.read_csv(DATA_URL).to_csv(LOCAL_FILE, index=False)
    df = pd.read_csv(LOCAL_FILE, usecols=["country", "year", "co2_per_capita"])
    return df


def prepare(df: pd.DataFrame):
    sub = df[df["country"].isin(COUNTRIES) & (df["year"] >= START_YEAR)]
    wide = sub.pivot(index="year", columns="country", values="co2_per_capita")
    wide = wide.dropna(how="all")
    # latest year in which every selected country has a value
    end_year = int(wide.dropna().index.max())
    wide = wide.loc[:end_year]

    world = df[(df["country"] == "World") & (df["year"] == end_year)]
    world_avg = float(world["co2_per_capita"].iloc[0])

    missing = sorted(set(COUNTRIES) - set(wide.columns))
    if missing:
        print("Warning - not found in data:", missing)
    return wide, end_year, world_avg


def spread_labels(values: dict, min_gap: float) -> dict:
    """Nudge label y-positions apart so end labels never overlap."""
    items = sorted(values.items(), key=lambda kv: kv[1])
    placed = {}
    last = None
    for name, y in items:
        if last is not None and y - last < min_gap:
            y = last + min_gap
        placed[name] = y
        last = y
    return placed


# --------------------------------------------------------------------------
# Shared styling for the improved charts
# --------------------------------------------------------------------------
def clean_axes(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(GREY)
    ax.spines["bottom"].set_color(GREY)
    ax.tick_params(colors=DARK, labelsize=10)


def add_titles(fig, title, subtitle, source):
    fig.text(0.02, 0.97, title, fontsize=15, fontweight="bold",
             color=DARK, ha="left", va="top")
    fig.text(0.02, 0.915, subtitle, fontsize=10.5, color="#666666",
             ha="left", va="top")
    fig.text(0.02, 0.015, source, fontsize=8, color="#888888", ha="left")


SOURCE = "Source: Our World in Data / Global Carbon Project (owid/co2-data)."


# --------------------------------------------------------------------------
# Figure 0 - baseline: matplotlib defaults, nothing changed on purpose
# --------------------------------------------------------------------------
def fig0_baseline(wide):
    plt.figure()
    for country in wide.columns:
        plt.plot(wide.index, wide[country], label=country)
    plt.legend()
    plt.savefig(OUT_DIR / "fig0_baseline.png")
    plt.close()


# --------------------------------------------------------------------------
# Figure 1 - highlighted line chart
# --------------------------------------------------------------------------
def fig1_highlight_line(wide, end_year):
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.subplots_adjust(top=0.82, bottom=0.10, left=0.07, right=0.78)

    for country in wide.columns:
        if country not in HIGHLIGHT:
            ax.plot(wide.index, wide[country], color=GREY, lw=1, alpha=0.7)

    shown = {c: wide[c].iloc[-1] for c in HIGHLIGHT if c in wide.columns}
    gap = 0.045 * wide.max().max()
    label_y = spread_labels(shown, gap)
    for country, y_end in shown.items():
        colour = HIGHLIGHT[country]
        ax.plot(wide.index, wide[country], color=colour, lw=2.8)
        ax.text(end_year + 0.6, label_y[country], f"{country}  {y_end:.1f} t",
                color=colour, fontsize=10, fontweight="bold", va="center")

    ax.set_xlim(START_YEAR, end_year)
    ax.set_ylabel("Tonnes of CO₂ per person", color=DARK)
    ax.yaxis.grid(True, color="#eeeeee")
    ax.set_axisbelow(True)
    clean_axes(ax)

    add_titles(
        fig,
        "China now emits more CO₂ per person than the UK",
        f"Per-capita CO₂ emissions, {START_YEAR}-{end_year}. "
        f"Grey lines: {len(wide.columns) - len(HIGHLIGHT)} other large economies.",
        SOURCE,
    )
    fig.savefig(OUT_DIR / "fig1_highlight_line.png", dpi=200)
    plt.close(fig)


# --------------------------------------------------------------------------
# Figure 2 - slope chart, start vs end year
# --------------------------------------------------------------------------
def fig2_slope(wide, end_year):
    start = wide.loc[START_YEAR]
    end = wide.loc[end_year]

    fig, ax = plt.subplots(figsize=(7.5, 8))
    fig.subplots_adjust(top=0.86, bottom=0.06, left=0.24, right=0.76)

    strong_set = [c for c in HIGHLIGHT if c in wide.columns]
    gap = 0.035 * max(start.max(), end.max())
    left_y = spread_labels({c: start[c] for c in strong_set}, gap)
    right_y = spread_labels({c: end[c] for c in strong_set}, gap)

    for country in wide.columns:
        rose = end[country] > start[country]
        colour = UP if rose else DOWN
        strong = country in HIGHLIGHT
        ax.plot([0, 1], [start[country], end[country]],
                color=colour, lw=2.6 if strong else 1.2,
                alpha=1 if strong else 0.45, marker="o", ms=4)
        if strong:
            ax.text(-0.04, left_y[country], f"{country} {start[country]:.1f}",
                    ha="right", va="center", fontsize=9.5, color=colour,
                    fontweight="bold")
            ax.text(1.04, right_y[country], f"{end[country]:.1f} {country}",
                    ha="left", va="center", fontsize=9.5, color=colour,
                    fontweight="bold")

    ax.set_xlim(-0.05, 1.05)
    ax.set_xticks([0, 1], [str(START_YEAR), str(end_year)],
                  fontsize=12, fontweight="bold")
    ax.set_yticks([])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GREY)

    n_up = int((end > start).sum())
    n_down = len(wide.columns) - n_up
    add_titles(
        fig,
        "Rich countries cut, emerging economies grew",
        f"Tonnes of CO₂ per person. "
        f"Red: rose ({n_up} countries). Blue: fell ({n_down} countries).",
        SOURCE,
    )
    fig.savefig(OUT_DIR / "fig2_slope.png", dpi=200)
    plt.close(fig)


# --------------------------------------------------------------------------
# Figure 3 - ranked horizontal bar chart with world average
# --------------------------------------------------------------------------
def fig3_ranked_bar(wide, end_year, world_avg):
    latest = wide.loc[end_year].sort_values()

    fig, ax = plt.subplots(figsize=(9, 8))
    fig.subplots_adjust(top=0.86, bottom=0.08, left=0.18, right=0.95)

    colours = [UP if v > world_avg else GREY for v in latest.values]
    bars = ax.barh(latest.index, latest.values, color=colours, height=0.7)

    for bar, value in zip(bars, latest.values):
        ax.text(value + 0.2, bar.get_y() + bar.get_height() / 2,
                f"{value:.1f}", va="center", fontsize=9, color=DARK)

    ax.axvline(world_avg, color=DARK, lw=1.2, ls="--")
    ax.text(world_avg + 0.2, len(latest) - 0.4,
            f"World average {world_avg:.1f} t", fontsize=9.5, color=DARK,
            va="bottom")

    ax.set_xlabel("Tonnes of CO₂ per person", color=DARK)
    ax.tick_params(axis="y", length=0)
    clean_axes(ax)
    ax.spines["left"].set_visible(False)

    n_above = int((latest > world_avg).sum())
    add_titles(
        fig,
        f"{n_above} of {len(latest)} large economies emit above the world average",
        f"CO₂ emissions per person, {end_year}. Red: above world average.",
        SOURCE,
    )
    fig.savefig(OUT_DIR / "fig3_ranked_bar.png", dpi=200)
    plt.close(fig)


# --------------------------------------------------------------------------
def main():
    OUT_DIR.mkdir(exist_ok=True)
    df = load_data()
    wide, end_year, world_avg = prepare(df)
    print(f"Years {START_YEAR}-{end_year}, {len(wide.columns)} countries, "
          f"world average {world_avg:.2f} t")

    fig0_baseline(wide)                      # matplotlib defaults only
    with plt.rc_context(IMPROVED_RC):        # Arial for the redesigns
        fig1_highlight_line(wide, end_year)
        fig2_slope(wide, end_year)
        fig3_ranked_bar(wide, end_year, world_avg)
    print("Saved figures to", OUT_DIR.resolve())
    print_numbers_for_text(wide, end_year, world_avg)


def print_numbers_for_text(wide, end_year, world_avg):
    """Print every number the written assignment refers to."""
    start, end = wide.loc[START_YEAR], wide.loc[end_year]
    print("\n=== Numbers for the written assignment ===")
    print(f"Latest complete year: {end_year}")
    print(f"World average {end_year}: {world_avg:.1f} t")
    print(f"Countries above world average: {int((end > world_avg).sum())} of {len(end)}")
    print(f"Countries that rose since {START_YEAR}: {int((end > start).sum())}; "
          f"fell: {int((end <= start).sum())}")
    if {"China", "United Kingdom"} <= set(wide.columns):
        crossed = wide.index[wide["China"] > wide["United Kingdom"]]
        if len(crossed):
            print(f"First year China > United Kingdom: {int(crossed[0])}")
    print(f"\n{'Country':<16}{START_YEAR:>8}{end_year:>8}{'change':>9}")
    for c in end.sort_values(ascending=False).index:
        pct = (end[c] / start[c] - 1) * 100
        print(f"{c:<16}{start[c]:>8.1f}{end[c]:>8.1f}{pct:>8.0f}%")


if __name__ == "__main__":
    main()
