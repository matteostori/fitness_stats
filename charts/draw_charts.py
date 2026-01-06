import matplotlib.pyplot as plt

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

def draw_weekly(df):
    # df = df.dropna(subset=["kcals daily avg"])        
    #
    # fig, ax1 = plt.subplots()
    # ax2 = ax1.twinx()
    #
    # bars = ax1.bar(df["Yearweek"].astype(str), df["kcals daily avg"], label="kcals daily avg")
    # ax1.bar_label(bars, labels=[f"{v:,.2f}" for v in df["kcals daily avg"]], padding=4, fontsize=8)
    # ax1.set_ylabel("kcals daily avg")
    #
    # ax2.plot(df["Yearweek"].astype(str), df["Weight avg kg"], marker="o", color='gray', label="Weight avg kg")
    #
    # # line point labels (weight)
    # for x, y in zip(df["Yearweek"].astype(str), df["Weight avg kg"]):
    #     ax2.text(
    #         x,
    #         y,
    #         f"{y:.2f}",
    #         color="red",
    #         ha="center",
    #         va="bottom",
    #         fontsize=8
    # )
    # ax2.set_ylabel("Weight avg kg")
    #
    # # Combine legends
    # lines1, labels1 = ax1.get_legend_handles_labels()
    # lines2, labels2 = ax2.get_legend_handles_labels()
    # ax1.legend(lines1 + lines2, labels1 + labels2)
    #
    # ax1.set_title("Weight avg kg and kcals daily avg")
    #
    # plt.tight_layout()
    # plt.xticks(rotation=45)
    # plt.show()

    line_color = "C1"
    bar_color = "C2"

    df = df.dropna(subset=["kcals daily avg"])        
    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax2 = ax1.twinx()
    
    x = df["Yearweek"].astype(str)
    
    bars = ax1.bar(x, df["kcals daily avg"], label="kcals daily avg", color=bar_color)
    ax2.plot(x, df["Weight avg kg"], marker="o", color=line_color, label="Weight avg kg")
    
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
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def draw_daily(df):
    pass