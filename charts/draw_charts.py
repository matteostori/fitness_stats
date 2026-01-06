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
    # get colors from palette
    bar_color = EXTENDED_PALETTE[0]
    line_color = EXTENDED_PALETTE[1]
    line_movingavg_color = EXTENDED_PALETTE[2]

    # clean data / manipulate data
    df = df.dropna(subset=["kcals daily avg"])
    # --- calculate 4-week rolling average of weight ---
    df["Weight_rolling4"] = df["Weight avg kg"].rolling(window=4, min_periods=1).mean()
    # --- calculate 4-week rolling average of kcals ---
    df["kcals_rolling4"] = df["kcals daily avg"].rolling(window=4, min_periods=1).mean()
 
    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax2 = ax1.twinx() # for double axis
    
    x = df["Yearweek"].astype(str) # to make sure we plot axis labels and show the bars/lines not empty
    
    bars = ax1.bar(x, df["kcals daily avg"], label="kcals daily avg", color=bar_color, alpha=0.85)
    ax1.plot(x, df["kcals_rolling4"], color=bar_color, linestyle="-", marker=None, label="kcals 4-wk MA")
    ax2.plot(x, df["Weight avg kg"], marker="o", color=line_color, label="Weight avg kg")
    ax2.plot(x, df["Weight_rolling4"], color=line_movingavg_color, linestyle="--", marker=None, label="Weight 4-wk MA")
    
    # bar labels
    ax1.bar_label(
        bars,
        color=bar_color,
        labels=[f"{v:,.2f}" for v in df["kcals daily avg"]],
        padding=3,
        fontsize=8
    )
    
    # line labels with collision avoidance
    label_line_points_smart(
        fig=fig,
        ax_line=ax2,
        ax_bar=ax1,
        x_values=x,
        line_values=df["Weight avg kg"],
        bars=bars,
        fmt="{:.1f}",
        color=line_color,
        fontsize=8,
        min_pixel_distance=12
    )
    
    ax1.set_ylabel("Daily avg kcals")
    ax2.set_ylabel("Weight avg kg")
    
    # rotate x-ticks on the bar axis
    ax1.tick_params(axis='x', rotation=45)
    
    ax1.grid(axis="y", alpha=0.2)
    plt.tight_layout()
    plt.show()

# def draw_weekly_lifts(df):
#     # --- convert kg to tons (already done) ---
#     df["Totals tons"] = df["Totals kg"] / 1000 
#     df["Leg tons"] = df["Leg kg"] / 1000 
#     df["Chest tons"] = df["Chest kg"] / 1000 
#     df["Back tons"] = df["Back kg"] / 1000 
#     df["Shoulders tons"] = df["Shoulders kg"] / 1000 
#     df["Biceps tons"] = df["Biceps kg"] / 1000 
#     df["Core tons"] = df["Core kg"] / 1000 
#
#     muscle_groups = ["Leg tons", "Chest tons", "Back tons", "Shoulders tons", "Biceps tons", "Core tons"]
#     df = df.dropna(subset=muscle_groups + ["Yearweek"])
#     df = df.sort_values("Yearweek")
#     x = df["Yearweek"].astype(str)
#
#     # --- consistent color palette ---
#     palette = {
#         "Leg tons": "#1f77b4",
#         "Chest tons": "#ff7f0e",
#         "Back tons": "#2ca02c",
#         "Shoulders tons": "#d62728",
#         "Biceps tons": "#9467bd",
#         "Core tons": "#8c564b"
#     }
#     colors = [palette[mg] for mg in muscle_groups]
#
#     # --- figure with 2 subplots ---
#     fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14,10), sharex=True)
#
#     # --------------------------
#     # TOP: Absolute stacked bars
#     # --------------------------
#     bottom = np.zeros(len(df))
#     bars_list = []
#
#     for mg, color in zip(muscle_groups, colors):
#         bars = ax1.bar(x, df[mg], bottom=bottom, label=mg, color=color, alpha=0.85)
#         bars_list.append(bars)
#
#         # --- labels inside bar segments if ≥5% and val>0 ---
#         for bar, val, total in zip(bars, df[mg], df["Totals tons"]):
#             if total > 0 and val / total >= 0.05 and val > 0:
#                 ax1.text(
#                     bar.get_x() + bar.get_width() / 2,
#                     bar.get_y() + val / 2,
#                     f"{val:.1f}",
#                     ha="center",
#                     va="center",
#                     fontsize=6,
#                     color="white"
#                 )
#         bottom += df[mg]
#
#     # --- total tons line (skip zero values in labels) ---
#     line_values = df["Totals tons"].values
#     ax1.plot(x, line_values, color="grey", marker="o", label="Total tons/week", linewidth=0.75)
#
#     # --- total tons text labels above bars (skip zero) ---
#     for xi, total in zip(x, line_values):
#         if total > 0:
#             ax1.text(
#                 xi,
#                 total + 0.5,  # offset above bar
#                 f"{total:.1f}",
#                 ha="center",
#                 va="bottom",
#                 fontsize=7,
#                 color="grey"
#             )
#
#     ax1.set_ylabel("Weight lifted (tons)")
#     ax1.set_title("Weekly Muscle Group Volume (Absolute)")
#     ax1.grid(axis="y", alpha=0.2)
#     ax1.legend(loc="upper left")
#
#     # --------------------------
#     # BOTTOM: Normalized stacked bars (%)
#     # --------------------------
#     normalized = df[muscle_groups].div(df["Totals tons"], axis=0)
#     bottom = np.zeros(len(df))
#     for mg, color in zip(muscle_groups, colors):
#         bars = ax2.bar(x, normalized[mg], bottom=bottom, label=mg, color=color, alpha=0.85)
#
#         # --- add % labels inside each segment if >5% ---
#         for bar, val in zip(bars, normalized[mg]):
#             if val >= 0.05:
#                 ax2.text(
#                     bar.get_x() + bar.get_width() / 2,
#                     bar.get_y() + val / 2,
#                     f"{val*100:.0f}%",
#                     ha="center",
#                     va="center",
#                     fontsize=6,
#                     color="white"
#                 )
#         bottom += normalized[mg]
#
#     ax2.set_ylabel("Relative contribution (%)")
#     ax2.set_title("Weekly Muscle Group Volume (Normalized %)")
#     ax2.grid(axis="y", alpha=0.2)
#     ax2.legend(loc="upper left")
#
#     # --------------------------
#     # Shared formatting
#     # --------------------------
#     plt.xticks(rotation=45, fontsize=8)
#     plt.xlabel("Week")
#
#     # --- add padding / margins ---
#     # absolute chart
#     ax1.set_ylim(0, df["Totals tons"].max()*1.1)
#     ax1.margins(y=0.05)
#
#     # normalized chart
#     ax2.set_ylim(0, 1.05)
#     ax2.margins(y=0.02)
#
#     # spacing between subplots and figure margins
#     plt.subplots_adjust(top=0.92, bottom=0.12, left=0.08, right=0.95, hspace=0.35)    
#     plt.show()

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
        df_copy = df_copy.set_index("Date").resample("Q").sum()
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
    plt.subplots_adjust(top=0.92, bottom=0.12, left=0.08, right=0.95, hspace=0.35)
    
# --------------------------
# Main function
# --------------------------
def draw_weekly_and_quarterly_lift_charts(df):
    # --- convert kg to tons ---
    df["Totals tons"] = df["Totals kg"] / 1000 
    df["Leg tons"] = df["Leg kg"] / 1000 
    df["Chest tons"] = df["Chest kg"] / 1000 
    df["Back tons"] = df["Back kg"] / 1000 
    df["Shoulders tons"] = df["Shoulders kg"] / 1000 
    df["Biceps tons"] = df["Biceps kg"] / 1000 
    df["Core tons"] = df["Core kg"] / 1000 
    
    # --- Weekly chart ---
    df_weekly = prepare_totals(df, muscle_groups, freq="W")
    plot_stacked_bars(df_weekly, muscle_groups, palette, title_suffix="(Weekly)")
    
    # --- Quarterly chart ---
    df_quarterly = prepare_totals(df, muscle_groups, freq="Q")
    plot_stacked_bars(df_quarterly, muscle_groups, palette, title_suffix="(Quarterly)")

    plt.show()

def draw_daily(df):
    pass