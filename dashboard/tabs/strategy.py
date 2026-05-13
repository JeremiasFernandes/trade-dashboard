from dash import html, dcc
import pandas as pd
from dashboard.data import compute_stats
from dashboard.kpi import kpi_card, kpi_row
from dashboard.charts import strategy_equity_overlay, strategy_comparison_bars, exit_reason_pie
from dashboard.theme import COLORS, STRATEGY_COLORS


def layout(df: pd.DataFrame):
    if df.empty:
        return html.Div("No closed trades.", style={"color": COLORS["text_muted"], "padding": "40px"})

    strategies = df["strategy_type"].unique()
    kpi_cards = []
    for st in strategies:
        sub = df[df["strategy_type"] == st]
        s = compute_stats(sub)
        color = STRATEGY_COLORS.get(st, COLORS["text"])
        kpi_cards.extend([
            kpi_card(f"{st.upper()} PnL", s["total_pnl"], prefix="$",
                     color=color, subtitle=f"{s['total_trades']} trades"),
            kpi_card(f"{st.upper()} Win Rate", s["win_rate"], suffix="%", color=color),
            kpi_card(f"{st.upper()} Avg R", s["avg_r_multiple"], suffix="R", color=color),
        ])

    return html.Div([
        kpi_row(kpi_cards),

        html.Div(style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}, children=[
            html.Div(style={"flex": "2", "minWidth": "500px"}, children=[
                dcc.Graph(figure=strategy_equity_overlay(df), config={"displayModeBar": False}),
            ]),
            html.Div(style={"flex": "1", "minWidth": "300px"}, children=[
                dcc.Graph(figure=exit_reason_pie(df), config={"displayModeBar": False}),
            ]),
        ]),

        dcc.Graph(figure=strategy_comparison_bars(df), config={"displayModeBar": False}),

        # Per-strategy exit reasons
        html.Div(style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}, children=[
            html.Div(style={"flex": "1", "minWidth": "300px"}, children=[
                html.H4(f"{st.upper()} Exit Reasons",
                         style={"color": STRATEGY_COLORS.get(st, COLORS["text"]),
                                "fontSize": "14px", "marginTop": "20px"}),
                dcc.Graph(
                    figure=exit_reason_pie(df[df["strategy_type"] == st]),
                    config={"displayModeBar": False},
                ),
            ])
            for st in strategies
        ]),
    ])
