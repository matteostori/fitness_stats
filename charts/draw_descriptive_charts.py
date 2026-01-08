import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

EXTENDED_PALETTE = [
    "#9ecae1",  # light blue 
    "#ff7f0e",  # orange
    "#8c564b",  # brown
    "#1f77b4",  # blue
    "#2ca02c",  # green
    "#9467bd",  # purple
    "#d62728",  # red
    "#7f7f7f"   # gray
]

muscle_groups = ["Leg tons", "Chest tons", "Back tons", "Shoulders tons", "Biceps tons", "Core tons"]
palette = {
    "Leg tons": "#1f77b4",
    "Chest tons": "#ff7f0e",
    "Back tons": "#2ca02c",
    "Shoulders tons": "#d62728",
    "Biceps tons": "#9467bd",
    "Core tons": "#8c564b"
}

def label_line_points_smart(
    fig,
    ax_line,
    ax_bar,
    x_values,
    line_values,
    bars,
    *,
    fmt="{:.2f}",
    color="red",
    fontsize=8,
    min_pixel_distance=12,
    pixel_offset=10
):
    """
    Add line-point labels while avoiding overlap with bar labels.
    Tries above the point, then below; hides label if both collide.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
    ax_line : matplotlib.axes.Axes
        Axis containing the line plot
    ax_bar : matplotlib.axes.Axes
        Axis containing the bar plot
    x_values : iterable
        X positions (same order as bars and line values)
    line_values : iterable
        Y values of the line
    bars : matplotlib.container.BarContainer
        Bars to check collisions against
    fmt : str
        Label format string
    color : str
        Label color
    fontsize : int
        Font size
    min_pixel_distance : int
        Minimum vertical pixel distance to avoid collision
    pixel_offset : int
        Pixel offset applied when shifting label up/down
    """

    fig.canvas.draw()

    for x, y, bar in zip(x_values, line_values, bars):

        # bar top (pixel coords)
        bar_top_disp = ax_bar.transData.transform(
            (bar.get_x() + bar.get_width() / 2, bar.get_height())
        )

        # line point (pixel coords)
        line_disp = ax_line.transData.transform((x, y))

        # try ABOVE
        above_disp_y = line_disp[1] + pixel_offset
        if abs(above_disp_y - bar_top_disp[1]) >= min_pixel_distance:
            ax_line.annotate(
                fmt.format(y),
                (x, y),
                xytext=(0, pixel_offset),
                textcoords="offset pixels",
                ha="center",
                va="bottom",
                fontsize=fontsize,
                color=color
            )
            continue

        # try BELOW
        below_disp_y = line_disp[1] - pixel_offset
        if abs(below_disp_y - bar_top_disp[1]) >= min_pixel_distance:
            ax_line.annotate(
                fmt.format(y),
                (x, y),
                xytext=(0, -pixel_offset),
                textcoords="offset pixels",
                ha="center",
                va="top",
                fontsize=fontsize,
                color=color
            )
            continue

        # else: skip label (collision both ways)

def draw_weekly_weight_kcals(df):
    # --------------------------
    # COLORS (same hue, different intensity)
    # --------------------------
    resting_color = EXTENDED_PALETTE[0]        # darkest
    active_color = EXTENDED_PALETTE[0]          # same hue, lighter via alpha
    neutral_color = "#9e9e9e"                   # neutral grey for surplus/deficit

    line_color = EXTENDED_PALETTE[1]
    line_movingavg_color = line_color

    # --------------------------
    # CLEAN & TRANSFORM DATA
    # --------------------------
    df = df.dropna(subset=[
        "kcals daily avg",
        "Resting energy kcal",
        "Active energy kcal",
        "Weight avg kg"
    ])

    # convert resting & active to thousands (kcal → thousands kcal)
    df["Resting_k"] = df["Resting energy kcal"] / 1000
    df["Active_k"] = df["Active energy kcal"] / 1000

    # surplus / deficit (can be negative)
    df["Energy_surplus_k"] = df["kcals daily avg"] - (df["Resting_k"] + df["Active_k"])

    # rolling averages
    df["Weight_rolling4"] = df["Weight avg kg"].rolling(4, min_periods=1).mean()
    df["kcals_rolling4"] = df["kcals daily avg"].rolling(4, min_periods=1).mean()

    # --------------------------
    # FIGURE / AXES
    # --------------------------
    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax2 = ax1.twinx()

    x = df["Yearweek"].astype(str)

    # --------------------------
    # STACKED BARS
    # --------------------------
    bottom_pos = np.zeros(len(df))
    bottom_neg = np.zeros(len(df))

    # Resting (always positive)
    bars_rest = ax1.bar(
        x,
        df["Resting_k"],
        bottom=bottom_pos,
        label="Resting energy kcal",
        color=resting_color,
        alpha=0.9
    )
    bottom_pos += df["Resting_k"]

    # Active (always positive, lighter)
    bars_active = ax1.bar(
        x,
        df["Active_k"],
        bottom=bottom_pos,
        label="Active energy kcal",
        color=active_color,
        alpha=0.55
    )
    bottom_pos += df["Active_k"]

    # Surplus / deficit (neutral color, can be negative)
    surplus_pos = df["Energy_surplus_k"].clip(lower=0)
    surplus_neg = df["Energy_surplus_k"].clip(upper=0)

    bars_surplus_pos = ax1.bar(
        x,
        surplus_pos,
        bottom=bottom_pos,
        label="Surplus / deficit kcal",
        color=neutral_color,
        alpha=0.8
    )

    bars_surplus_neg = ax1.bar(
        x,
        surplus_neg,
        bottom=bottom_neg,
        color=neutral_color,
        alpha=0.8
    )

    # ---------------------------------------
    # SEGMENT LABELS (inside stacks + on top)
    # --------------------------------------
    def label_segments(ax, bars, values, totals, min_frac=0.06):
        for bar, val, total in zip(bars, values, totals):
            if total > 0 and abs(val) / total >= min_frac:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}",
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="white"
                )
    def label_totals_on_top(ax, x, totals, y_offset_frac=0.015, fontsize=7):
        y_min, y_max = ax.get_ylim()
        y_offset = (y_max - y_min) * y_offset_frac
    
        for xi, total in zip(x, totals):
            ax.text(
                xi,
                total + y_offset,
                f"{total:.2f}",
                ha="center",
                va="bottom",
                fontsize=fontsize,
                color="grey"
            )            

    
    totals_k = df["kcals daily avg"]

    label_segments(ax1, bars_rest, df["Resting_k"], totals_k)
    label_segments(ax1, bars_active, df["Active_k"], totals_k)
    label_segments(ax1, bars_surplus_pos, surplus_pos, totals_k)

    # --------------------------
    # KCALS MOVING AVERAGE
    # --------------------------
    ax1.plot(
        x,
        df["kcals_rolling4"],
        color=resting_color,
        linewidth=1.3,
        label="kcals 4-wk MA"
    )

    # --------------------------
    # WEIGHT LINES (SECOND AXIS)
    # --------------------------
    ax2.plot(
        x,
        df["Weight avg kg"],
        marker="o",
        color=line_color,
        label="Weight avg kg"
    )

    ax2.plot(
        x,
        df["Weight_rolling4"],
        linestyle="--",
        color=line_movingavg_color,
        label="Weight 4-wk MA"
    )

    # --------------------------
    # Y-LIMITS (CORRECT FOR STACKED + NEGATIVE)
    # --------------------------
    max_stack = (df["Resting_k"] + df["Active_k"] + surplus_pos).max()
    min_stack = surplus_neg.min()

    ax1.set_ylim(min_stack * 1.2, max_stack * 1.15)
    ax1.margins(y=0.05)
    
    # --------------------------
    # TOTAL LABELS ON TOP
    # --------------------------
    total_stack = df["Resting_k"] + df["Active_k"] + surplus_pos
    label_totals_on_top(ax1, x, total_stack)

    # --------------------------
    # AXES & LAYOUT
    # --------------------------
    ax1.set_ylabel("Daily energy kcal")
    ax2.set_ylabel("Weight avg kg")

    ax1.tick_params(axis="x", rotation=45, labelsize=8)
    ax1.grid(axis="y", alpha=0.2)

    ax1.set_title("Daily Energy Breakdown (Resting / Active / Surplus) vs Weight")

    ax1.legend(loc="upper left", fontsize=8)
    ax2.legend(loc="upper right", fontsize=8)

    plt.tight_layout()

# --------------------------
# Helper 1: Prepare totals
# --------------------------
def prepare_totals(df, muscle_groups, freq="W"):
    """
    Aggregates totals by week ('W') or quarter ('Q').
    Returns a new dataframe with aggregated muscle groups and total.
    """
    df_copy = df.copy()
    if freq == "Q":
        # Assume df has Yearweek in ISO week format: convert to datetime first
        df_copy["Date"] = df_copy["Yearweek"].apply(lambda yw: pd.to_datetime(f"{str(yw)[:4]}-W{int(str(yw)[4:]):02d}-1", format="%G-W%V-%u"))
        df_copy = df_copy.set_index("Date").resample("QE").sum()
        # Quarter label for x-axis
        df_copy["Period"] = df_copy.index.to_period("Q").astype(str)
    else:
        # Weekly
        df_copy["Period"] = df_copy["Yearweek"].astype(str)
    
    # Compute total
    df_copy["Totals tons"] = df_copy[muscle_groups].sum(axis=1)
    
    return df_copy

# --------------------------
# Helper 2: Plot stacked bars
# --------------------------
def plot_stacked_bars(df, muscle_groups, palette, title_suffix=""):
    """
    Plots absolute and normalized stacked bar charts for a given dataframe.
    """
    x = df["Period"].astype(str)
    
    # Colors
    colors = [palette[mg] for mg in muscle_groups]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14,10))
    
    # --- Absolute stacked bars ---
    bottom = np.zeros(len(df))
    for mg, color in zip(muscle_groups, colors):
        bars = ax1.bar(x, df[mg], bottom=bottom, label=mg, color=color, alpha=0.85)
        for bar, val, total in zip(bars, df[mg], df["Totals tons"]):
            if total > 0 and val / total >= 0.05 and val > 0:
                ax1.text(
                    bar.get_x() + bar.get_width()/2,
                    bar.get_y() + val/2,
                    f"{val:.1f}",
                    ha="center",
                    va="center",
                    fontsize=6,
                    color="white"
                )
        bottom += df[mg]
    
    # --- Total tons line ---
    line_values = df["Totals tons"].values
    ax1.plot(x, line_values, color="grey", marker="o", label="Total tons", linewidth=0.75)
    for xi, total in zip(x, line_values):
        if total > 0:
            ax1.text(
                xi,
                total + 0.5,
                f"{total:.1f}",
                ha="center",
                va="bottom",
                fontsize=7,
                color="grey"
            )
    
    ax1.set_ylabel("Weight lifted (tons)")
    ax1.set_title(f"Absolute Weekly Muscle Group Volume {title_suffix}")
    ax1.grid(axis="y", alpha=0.2)
    ax1.legend(loc="upper left", fontsize=8)
    ax1.tick_params(axis='x', rotation=45, labelsize=8)
    ax1.set_ylim(0, df["Totals tons"].max()*1.1)
    ax1.margins(y=0.05)
    
    # --- Normalized stacked bars (%)
    normalized = df[muscle_groups].div(df["Totals tons"], axis=0)
    bottom = np.zeros(len(df))
    for mg, color in zip(muscle_groups, colors):
        bars = ax2.bar(x, normalized[mg], bottom=bottom, label=mg, color=color, alpha=0.85)
        for bar, val in zip(bars, normalized[mg]):
            if val >= 0.05:
                ax2.text(
                    bar.get_x() + bar.get_width()/2,
                    bar.get_y() + val/2,
                    f"{val*100:.0f}%",
                    ha="center",
                    va="center",
                    fontsize=6,
                    color="white"
                )
        bottom += normalized[mg]
    
    ax2.set_ylabel("Relative contribution (%)")
    ax2.set_title(f"Normalized Muscle Group Volume {title_suffix}")
    ax2.grid(axis="y", alpha=0.2)
    ax2.legend(loc="upper left", fontsize=8)
    ax2.set_ylim(0, 1.05)
    ax2.margins(y=0.02)
    plt.xticks(rotation=45, size=8)
    plt.subplots_adjust(top=0.92, bottom=0.12, left=0.02, right=0.98, hspace=0.35)
    
# --------------------------
# Main function
# --------------------------
def draw_weekly_and_quarterly_lift_charts(df):
    # --- Weekly chart ---
    df_weekly = prepare_totals(df, muscle_groups, freq="W")
    plot_stacked_bars(df_weekly, muscle_groups, palette, title_suffix="(Weekly)")
    
    # --- Quarterly chart ---
    df_quarterly = prepare_totals(df, muscle_groups, freq="Q")
    plot_stacked_bars(df_quarterly, muscle_groups, palette, title_suffix="(Quarterly)")