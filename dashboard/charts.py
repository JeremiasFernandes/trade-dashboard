"""
Chart builder functions — Plotly figures reutilizaveis.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from .theme import COLORS, STRATEGY_COLORS, EXIT_REASON_COLORS


def _empty_fig(msg: str = "No data") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=msg, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
                       font=dict(size=16, color=COLORS["text_muted"]))
    fig.update_layout(height=300)
    return fig


def equity_curve(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_fig("No closed trades")

    fig = go.Figure()

    # Equity line
    fig.add_trace(go.Scatter(
        x=df["exit_time"], y=df["cumulative_pnl"],
        mode="lines", name="Equity",
        line=dict(color=COLORS["blue"], width=2),
        fill="tozeroy",
        fillcolor="rgba(88, 166, 255, 0.08)",
        hovertemplate="PnL: %{y:.4f}<br>%{x}<extra></extra>",
    ))

    # Peak line
    fig.add_trace(go.Scatter(
        x=df["exit_time"], y=df["peak"],
        mode="lines", name="Peak",
        line=dict(color=COLORS["text_muted"], width=1, dash="dot"),
        hoverinfo="skip",
    ))

    fig.update_layout(
        title="Equity Curve",
        xaxis_title="", yaxis_title="Cumulative PnL",
        height=350, showlegend=False,
    )
    return fig


def drawdown_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_fig()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["exit_time"], y=df["drawdown"],
        mode="lines", name="Drawdown",
        line=dict(color=COLORS["red"], width=1.5),
        fill="tozeroy",
        fillcolor="rgba(248, 81, 73, 0.15)",
        hovertemplate="DD: %{y:.4f}<extra></extra>",
    ))
    fig.update_layout(
        title="Drawdown", height=200,
        xaxis_title="", yaxis_title="Drawdown",
        showlegend=False,
    )
    return fig


def pnl_distribution(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_fig()

    winners = df[df["net_pnl"] > 0]["net_pnl"]
    losers = df[df["net_pnl"] <= 0]["net_pnl"]

    fig = go.Figure()
    if not losers.empty:
        fig.add_trace(go.Histogram(
            x=losers, name="Losers", marker_color=COLORS["red"],
            opacity=0.7, nbinsx=20,
        ))
    if not winners.empty:
        fig.add_trace(go.Histogram(
            x=winners, name="Winners", marker_color=COLORS["green"],
            opacity=0.7, nbinsx=20,
        ))
    fig.update_layout(
        title="PnL Distribution", barmode="overlay",
        xaxis_title="Net PnL", yaxis_title="Count", height=300,
    )
    return fig


def r_multiple_distribution(df: pd.DataFrame) -> go.Figure:
    if df.empty or "r_multiple" not in df:
        return _empty_fig()

    vals = df["r_multiple"].dropna()
    if vals.empty:
        return _empty_fig("No R-multiple data")

    colors = [COLORS["green"] if v > 0 else COLORS["red"] for v in vals]

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=vals, nbinsx=30, name="R-Multiple",
        marker_color=COLORS["blue"], opacity=0.8,
    ))

    mean_r = vals.mean()
    fig.add_vline(x=mean_r, line_dash="dash", line_color=COLORS["orange"],
                  annotation_text=f"Avg: {mean_r:.2f}R")
    fig.add_vline(x=0, line_color=COLORS["text_muted"], line_width=1)

    fig.update_layout(
        title="R-Multiple Distribution",
        xaxis_title="R-Multiple", yaxis_title="Count", height=300,
    )
    return fig


def win_rate_rolling(df: pd.DataFrame, window: int = 20) -> go.Figure:
    if df.empty or len(df) < window:
        return _empty_fig(f"Need {window}+ trades")

    sorted_df = df.sort_values("exit_time")
    rolling = sorted_df["is_winner"].rolling(window).mean() * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sorted_df["exit_time"], y=rolling,
        mode="lines", name=f"Win Rate ({window}-trade)",
        line=dict(color=COLORS["cyan"], width=2),
    ))
    fig.add_hline(y=50, line_dash="dash", line_color=COLORS["text_muted"])

    fig.update_layout(
        title=f"Rolling Win Rate ({window} trades)",
        xaxis_title="", yaxis_title="Win Rate %", height=300,
        yaxis=dict(range=[0, 100]),
    )
    return fig


def cumulative_r(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_fig()

    sorted_df = df.sort_values("exit_time")
    cum_r = sorted_df["r_multiple"].cumsum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(1, len(cum_r) + 1)), y=cum_r,
        mode="lines", name="Cumulative R",
        line=dict(color=COLORS["green"], width=2),
        fill="tozeroy", fillcolor="rgba(63, 185, 80, 0.08)",
    ))
    fig.update_layout(
        title="Cumulative R-Multiple",
        xaxis_title="Trade #", yaxis_title="Cumulative R", height=300,
    )
    return fig


# === MFE / MAE ===

def mfe_vs_mae_scatter(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_fig()

    fig = go.Figure()
    for label, color in [("Winner", COLORS["green"]), ("Loser", COLORS["red"])]:
        sub = df[df["result_label"] == label]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["mfe_pct"] * 100, y=sub["mae_pct"] * 100,
            mode="markers", name=label,
            marker=dict(color=color, size=8, opacity=0.7, line=dict(width=1, color=COLORS["border"])),
            hovertemplate=(
                "%{customdata[0]}<br>"
                "MFE: %{x:.2f}%<br>MAE: %{y:.2f}%<br>"
                "PnL: %{customdata[1]:.4f}<extra></extra>"
            ),
            customdata=sub[["symbol", "net_pnl"]].values,
        ))

    fig.update_layout(
        title="MFE vs MAE",
        xaxis_title="MFE %", yaxis_title="MAE %", height=400,
    )
    return fig


def mfe_vs_pnl_scatter(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_fig()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["mfe_pct"] * 100, y=df["net_pnl"],
        mode="markers", name="Trades",
        marker=dict(
            color=[COLORS["green"] if w else COLORS["red"] for w in df["is_winner"]],
            size=8, opacity=0.7,
        ),
        hovertemplate="MFE: %{x:.2f}%<br>PnL: %{y:.4f}<extra></extra>",
    ))

    fig.update_layout(
        title="MFE vs PnL (left money on the table?)",
        xaxis_title="MFE %", yaxis_title="Net PnL", height=400,
    )
    return fig


def exit_efficiency_dist(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_fig()

    vals = df["exit_efficiency"].dropna()
    vals = vals[(vals > -5) & (vals < 5)]
    if vals.empty:
        return _empty_fig()

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=vals * 100, nbinsx=30, name="Exit Efficiency",
        marker_color=COLORS["cyan"], opacity=0.8,
    ))

    mean_eff = vals.mean() * 100
    fig.add_vline(x=mean_eff, line_dash="dash", line_color=COLORS["orange"],
                  annotation_text=f"Avg: {mean_eff:.1f}%")

    fig.update_layout(
        title="Exit Efficiency Distribution",
        xaxis_title="Exit Efficiency %", yaxis_title="Count", height=300,
    )
    return fig


# === STRATEGY ===

def strategy_equity_overlay(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_fig()

    fig = go.Figure()
    for st in df["strategy_type"].unique():
        sub = df[df["strategy_type"] == st].sort_values("exit_time")
        cum = sub["net_pnl"].cumsum()
        color = STRATEGY_COLORS.get(st, COLORS["blue"])
        fig.add_trace(go.Scatter(
            x=sub["exit_time"], y=cum,
            mode="lines", name=st.upper(),
            line=dict(color=color, width=2),
        ))

    fig.update_layout(
        title="Equity by Strategy",
        xaxis_title="", yaxis_title="Cumulative PnL", height=350,
    )
    return fig


def strategy_comparison_bars(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_fig()

    rows = []
    for st in df["strategy_type"].unique():
        sub = df[df["strategy_type"] == st]
        w = sub[sub["net_pnl"] > 0]
        wr = len(w) / len(sub) * 100 if len(sub) > 0 else 0
        rows.append({
            "Strategy": st.upper(),
            "Win Rate %": round(wr, 1),
            "Avg R": round(sub["r_multiple"].mean(), 2),
            "Avg PnL": round(sub["net_pnl"].mean(), 4),
            "Trades": len(sub),
        })

    comp = pd.DataFrame(rows)
    metrics = ["Win Rate %", "Avg R", "Avg PnL"]

    fig = go.Figure()
    for _, row in comp.iterrows():
        st = row["Strategy"]
        color = STRATEGY_COLORS.get(st.lower(), COLORS["blue"])
        fig.add_trace(go.Bar(
            x=metrics,
            y=[row[m] for m in metrics],
            name=f"{st} ({row['Trades']} trades)",
            marker_color=color, opacity=0.85,
        ))

    fig.update_layout(
        title="Strategy Comparison",
        barmode="group", height=350,
        yaxis_title="Value",
    )
    return fig


def exit_reason_pie(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_fig()

    counts = df["exit_reason"].value_counts()
    colors = [EXIT_REASON_COLORS.get(r, COLORS["text_muted"]) for r in counts.index]

    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values,
        marker=dict(colors=colors),
        hole=0.45, textinfo="label+percent",
        textfont=dict(size=11),
    ))
    fig.update_layout(title="Exit Reasons", height=350, showlegend=False)
    return fig


# === REGIME ===

def regime_scatter(df: pd.DataFrame, x_col: str, x_label: str) -> go.Figure:
    if df.empty or x_col not in df:
        return _empty_fig()

    fig = go.Figure()
    for label, color in [("Winner", COLORS["green"]), ("Loser", COLORS["red"])]:
        sub = df[df["result_label"] == label]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub[x_col], y=sub["net_pnl"],
            mode="markers", name=label,
            marker=dict(color=color, size=7, opacity=0.6),
            hovertemplate=f"{x_label}: %{{x:.4f}}<br>PnL: %{{y:.4f}}<extra></extra>",
        ))

    fig.add_hline(y=0, line_color=COLORS["text_muted"], line_width=1)
    fig.update_layout(
        title=f"{x_label} at Entry vs PnL",
        xaxis_title=x_label, yaxis_title="Net PnL", height=350,
    )
    return fig


def btc_regime_bars(df: pd.DataFrame) -> go.Figure:
    if df.empty or "btc_return_during_trade" not in df:
        return _empty_fig()

    vals = df["btc_return_during_trade"].dropna()
    if vals.empty:
        return _empty_fig("No BTC data")

    df = df.copy()
    df["btc_regime"] = pd.cut(
        df["btc_return_during_trade"],
        bins=[-np.inf, -0.02, -0.005, 0.005, 0.02, np.inf],
        labels=["BTC < -2%", "BTC -2..0%", "BTC Flat", "BTC 0..+2%", "BTC > +2%"],
    )

    grouped = df.groupby("btc_regime", observed=True).agg(
        avg_pnl=("net_pnl", "mean"),
        count=("net_pnl", "count"),
    ).reset_index()

    colors = [COLORS["red"], COLORS["orange"], COLORS["text_muted"], COLORS["cyan"], COLORS["green"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped["btc_regime"].astype(str),
        y=grouped["avg_pnl"],
        marker_color=colors[:len(grouped)],
        text=[f"n={c}" for c in grouped["count"]],
        textposition="outside",
    ))
    fig.add_hline(y=0, line_color=COLORS["text_muted"])
    fig.update_layout(
        title="Avg PnL by BTC Regime During Trade",
        xaxis_title="", yaxis_title="Avg Net PnL", height=350,
    )
    return fig


# === TIMING ===

def monthly_heatmap(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_fig()

    df = df.copy()
    df["year"] = df["exit_time"].dt.year
    df["month"] = df["exit_time"].dt.month

    pivot = df.groupby(["year", "month"])["net_pnl"].sum().reset_index()
    pivot_table = pivot.pivot(index="year", columns="month", values="net_pnl").fillna(0)

    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig = go.Figure(go.Heatmap(
        z=pivot_table.values,
        x=[month_labels[m - 1] for m in pivot_table.columns],
        y=pivot_table.index.astype(str),
        colorscale=[[0, COLORS["red"]], [0.5, COLORS["card"]], [1, COLORS["green"]]],
        zmid=0,
        text=np.round(pivot_table.values, 4),
        texttemplate="%{text:.4f}",
        textfont=dict(size=10),
        hovertemplate="PnL: %{z:.4f}<extra></extra>",
    ))

    fig.update_layout(
        title="Monthly Returns Heatmap",
        height=250, xaxis_title="", yaxis_title="",
    )
    return fig


def day_of_week_performance(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_fig()

    df = df.copy()
    df["dow"] = df["entry_time"].dt.dayofweek
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    grouped = df.groupby("dow").agg(
        avg_pnl=("net_pnl", "mean"),
        count=("net_pnl", "count"),
    ).reindex(range(7)).fillna(0)

    colors = [COLORS["green"] if v > 0 else COLORS["red"] for v in grouped["avg_pnl"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[day_names[i] for i in grouped.index],
        y=grouped["avg_pnl"],
        marker_color=colors,
        text=[f"n={int(c)}" for c in grouped["count"]],
        textposition="outside",
    ))
    fig.add_hline(y=0, line_color=COLORS["text_muted"])
    fig.update_layout(
        title="Avg PnL by Day of Week",
        xaxis_title="", yaxis_title="Avg PnL", height=300,
    )
    return fig


def hour_of_day_performance(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_fig()

    df = df.copy()
    df["hour"] = df["entry_time"].dt.hour

    grouped = df.groupby("hour").agg(
        avg_pnl=("net_pnl", "mean"),
        count=("net_pnl", "count"),
    ).reindex(range(24)).fillna(0)

    colors = [COLORS["green"] if v > 0 else COLORS["red"] for v in grouped["avg_pnl"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"{h:02d}h" for h in grouped.index],
        y=grouped["avg_pnl"],
        marker_color=colors,
    ))
    fig.add_hline(y=0, line_color=COLORS["text_muted"])
    fig.update_layout(
        title="Avg PnL by Hour (UTC)",
        xaxis_title="", yaxis_title="Avg PnL", height=300,
    )
    return fig


def duration_vs_pnl(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_fig()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["duration_hours"], y=df["net_pnl"],
        mode="markers",
        marker=dict(
            color=[COLORS["green"] if w else COLORS["red"] for w in df["is_winner"]],
            size=7, opacity=0.6,
        ),
        hovertemplate="Duration: %{x:.1f}h<br>PnL: %{y:.4f}<extra></extra>",
    ))
    fig.add_hline(y=0, line_color=COLORS["text_muted"])
    fig.update_layout(
        title="Trade Duration vs PnL",
        xaxis_title="Duration (hours)", yaxis_title="Net PnL", height=350,
    )
    return fig


def slippage_distribution(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_fig()

    vals = df["slippage"].dropna()
    vals = vals[vals > 0]
    if vals.empty:
        return _empty_fig("No slippage data")

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=vals * 100, nbinsx=25,
        marker_color=COLORS["orange"], opacity=0.8,
    ))
    fig.update_layout(
        title="Slippage Distribution",
        xaxis_title="Slippage %", yaxis_title="Count", height=300,
    )
    return fig


def funding_vs_pnl(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_fig()

    vals = df[df["funding_rate"] != 0]
    if vals.empty:
        return _empty_fig("No funding data")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=vals["funding_rate"] * 100, y=vals["net_pnl"],
        mode="markers",
        marker=dict(
            color=[COLORS["green"] if w else COLORS["red"] for w in vals["is_winner"]],
            size=7, opacity=0.6,
        ),
        hovertemplate="Funding: %{x:.4f}%<br>PnL: %{y:.4f}<extra></extra>",
    ))
    fig.add_hline(y=0, line_color=COLORS["text_muted"])
    fig.add_vline(x=0, line_color=COLORS["text_muted"])
    fig.update_layout(
        title="Funding Rate at Entry vs PnL",
        xaxis_title="Funding Rate %", yaxis_title="Net PnL", height=350,
    )
    return fig
