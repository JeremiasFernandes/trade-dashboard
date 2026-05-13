from dash import html, dcc
import pandas as pd
from dashboard.data import compute_stats
from dashboard.kpi import kpi_card, kpi_row
from dashboard.charts import mfe_vs_mae_scatter, mfe_vs_pnl_scatter, exit_efficiency_dist, slippage_distribution
from dashboard.theme import COLORS


def layout(df: pd.DataFrame):
    stats = compute_stats(df)

    return html.Div([
        kpi_row([
            kpi_card("Avg MFE", stats["avg_mfe"], suffix="%", color=COLORS["cyan"]),
            kpi_card("Avg MAE", stats["avg_mae"], suffix="%", color=COLORS["orange"]),
            kpi_card("Avg Exit Efficiency", stats["avg_exit_efficiency"], suffix="%",
                     color=COLORS["green"] if stats["avg_exit_efficiency"] >= 50 else COLORS["orange"],
                     subtitle="PnL / MFE captured"),
            kpi_card("Best Trade", stats["best_trade"], prefix="$", color=COLORS["green"]),
            kpi_card("Worst Trade", stats["worst_trade"], prefix="$", color=COLORS["red"]),
        ]),

        html.Div(style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}, children=[
            html.Div(style={"flex": "1", "minWidth": "450px"}, children=[
                dcc.Graph(figure=mfe_vs_mae_scatter(df), config={"displayModeBar": False}),
            ]),
            html.Div(style={"flex": "1", "minWidth": "450px"}, children=[
                dcc.Graph(figure=mfe_vs_pnl_scatter(df), config={"displayModeBar": False}),
            ]),
        ]),

        html.Div(style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}, children=[
            html.Div(style={"flex": "1", "minWidth": "450px"}, children=[
                dcc.Graph(figure=exit_efficiency_dist(df), config={"displayModeBar": False}),
            ]),
            html.Div(style={"flex": "1", "minWidth": "450px"}, children=[
                dcc.Graph(figure=slippage_distribution(df), config={"displayModeBar": False}),
            ]),
        ]),
    ])
