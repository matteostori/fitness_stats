import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def compute_fatigue_proxy(df):
    """
    Fatigue proxy combining lifting, time, and running.
    Scaled to be comparable over time.
    """
    df = df.copy()

    df["Fatigue_raw"] = (
        df["Totals kg"] * 0.6 +
        df["Mins gym"] * 0.3 +
        df["km run"] * 10
    )

    # normalize (z-score)
    df["Fatigue"] = (df["Fatigue_raw"] - df["Fatigue_raw"].mean()) / df["Fatigue_raw"].std()

    return df

# def plot_fatigue_chart(df, fig):
#     ax_fatigue = fig.add_subplot(gs[1, 3])
#
#     ax_fatigue.plot(
#         df["Yearweek"].astype(str),
#         df["Fatigue"],
#         marker="o",
#         linewidth=1.2,
#         label="Fatigue index"
#     )
#
#     ax_fatigue.plot(
#         df["Yearweek"].astype(str),
#         df["Fatigue"].rolling(4, min_periods=1).mean(),
#         linestyle="--",
#         linewidth=1,
#         label="Fatigue 4-wk MA"
#     )
#
#     ax_fatigue.axhline(0, color="grey", linestyle="--", linewidth=0.8)
#     ax_fatigue.set_title("Fatigue Index Over Time")
#     ax_fatigue.set_ylabel("Fatigue (z-score)")
#     ax_fatigue.tick_params(axis="x", rotation=45)
#     ax_fatigue.legend(fontsize=8)
#     ax_fatigue.grid(alpha=0.2)


# =====================================================
# 1A — ENERGY vs WEIGHT CHANGE (SCATTER + REGRESSION)
# =====================================================
def plot_energy_vs_weight_change(df):
    df = df.sort_values("Yearweek").copy()
    df["Weight_change"] = df["Weight avg kg"].diff()

    fig, ax = plt.subplots(figsize=(7, 5))

    sns.regplot(
        x="Weekly total cal surplus (deficit)",
        y="Weight_change",
        data=df,
        ax=ax,
        scatter_kws={"alpha": 0.7},
        line_kws={"color": "red"}
    )

    ax.axhline(0, color="grey", linestyle="--", linewidth=0.8)
    ax.set_title("Caloric Surplus vs Weekly Weight Change")
    ax.set_xlabel("Weekly calorie surplus / deficit")
    ax.set_ylabel("Weekly weight change (kg)")
    ax.grid(alpha=0.2)

    plt.tight_layout()



# =====================================================
# 3B — RADAR CHART (MUSCLE BALANCE, MONTHLY / QUARTERLY)
# =====================================================
def plot_muscle_radar(df, freq="QE"):
    muscle_cols = ["Leg kg", "Shoulders kg", "Chest kg", "Biceps kg", "Back kg", "Core kg"]

    df = df.copy()
    df["date"] = pd.to_datetime(df["Year"].astype(str) + "-01-01") + \
                 pd.to_timedelta((df["Week"] - 1) * 7, unit="D")

    grouped = df.groupby(pd.Grouper(key="date", freq=freq))[muscle_cols].sum()
    grouped = grouped.div(grouped.sum(axis=1), axis=0)

    labels = muscle_cols
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    for idx, row in grouped.iterrows():
        values = row.tolist()
        values += values[:1]
        ax.plot(angles, values, alpha=0.6, label=str(idx.date()))
        ax.fill(angles, values, alpha=0.1)

    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_title(f"Muscle Group Balance ({freq})")
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=8)

    plt.tight_layout()



# =====================================================
# 4 — SETS vs KG + KG PER SET OVER TIME
# =====================================================
muscle_cols = ["Leg", "Shoulders", "Chest", "Biceps", "Back", "Core"]

def plot_sets_vs_load(df):
    for muscle in muscle_cols:
        plot_sets_vs_load_muscle(df, muscle)

def plot_sets_vs_load_muscle(df, muscle):
    kg_col = f"{muscle} kg"
    sets_col = f"{muscle} sets"

    df = df.dropna(subset=[kg_col, sets_col]).copy()
    df["kg_per_set"] = df[kg_col] / df[sets_col]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), sharex=True)

    # Scatter: sets vs kg
    sns.regplot(
        x=sets_col,
        y=kg_col,
        data=df,
        ax=ax1,
        scatter_kws={"alpha": 0.7}
    )
    ax1.set_title(f"{muscle}: Sets vs Total Load")
    ax1.set_xlabel("Sets")
    ax1.set_ylabel("Total kg")

    # Line: kg per set
    ax2.plot(df["Yearweek"].astype(str), df["kg_per_set"], marker="o")
    ax2.set_title(f"{muscle}: kg per set over time")
    ax2.set_ylabel("kg per set")
    ax2.tick_params(axis="x", rotation=45)

    plt.tight_layout()



# =====================================================
# 5 — RUNNING vs LIFTING TRADEOFFS
# =====================================================
def plot_running_vs_lifting(df):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Running vs lifting volume
    sns.scatterplot(
        x="km run",
        y="Totals kg",
        hue="Weekly total cal surplus (deficit)",
        data=df,
        ax=axes[0]
    )
    axes[0].set_title("Running Distance vs Lifting Volume")

    # Running vs weight change
    df = df.sort_values("Yearweek").copy()
    df["Weight_change"] = df["Weight avg kg"].diff()

    sns.scatterplot(
        x="km run",
        y="Weight_change",
        hue="Weekly total cal surplus (deficit)",
        data=df,
        ax=axes[1]
    )
    axes[1].axhline(0, color="grey", linestyle="--")
    axes[1].set_title("Running Distance vs Weight Change")

    plt.tight_layout()



# =====================================================
# 6 — PROTEIN ANALYSIS
# =====================================================
def plot_protein_effect(df):
    df = df.sort_values("Yearweek").copy()
    df["Weight_change"] = df["Weight avg kg"].diff()
    df["Protein_per_kg"] = df["Proteins daily avg"] / df["Weight avg kg"]

    fig, ax = plt.subplots(figsize=(7, 5))

    sns.regplot(
        x="Protein_per_kg",
        y="Weight_change",
        data=df,
        ax=ax
    )

    ax.set_title("Protein Intake per kg vs Weight Change")
    ax.set_xlabel("Protein (g / kg bodyweight)")
    ax.set_ylabel("Weekly weight change (kg)")
    ax.grid(alpha=0.2)

    plt.tight_layout()



# =====================================================
# 7 — PROJECTED vs ACTUAL WEIGHT (BOTH)
# =====================================================
def plot_projection_accuracy(df):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Time series
    axes[0].plot(df["Yearweek"].astype(str), df["Weight avg kg"], label="Actual")
    axes[0].plot(df["Yearweek"].astype(str), df["Projected weight kg"], linestyle="--", label="Projected")
    axes[0].set_title("Projected vs Actual Weight")
    axes[0].legend()
    axes[0].tick_params(axis="x", rotation=45, labelsize=6)

    # Scatter accuracy
    sns.scatterplot(
        x="Projected weight kg",
        y="Weight avg kg",
        data=df,
        ax=axes[1]
    )
    min_w = df[["Projected weight kg", "Weight avg kg"]].min().min()
    max_w = df[["Projected weight kg", "Weight avg kg"]].max().max()
    axes[1].plot([min_w, max_w], [min_w, max_w], linestyle="--", color="grey")
    axes[1].set_title("Prediction Accuracy")

    plt.tight_layout()


# =====================================================
# 9 — CORRELATION HEATMAP (OVERVIEW)
# =====================================================
def plot_correlation_heatmap(df):
    cols = [
        "kcals daily avg",
        "Weekly total cal surplus (deficit)",
        "Totals kg",
        "km run",
        "Mins gym",
        "Weight avg kg",
        "Proteins daily avg"
    ]

    corr = df[cols].corr()

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        corr,
        annot=True,
        cmap="coolwarm",
        center=0,
        ax=ax
    )

    ax.set_title("Correlation Overview")
    plt.tight_layout()
