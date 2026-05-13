from dash import html, dcc
import pandas as pd
from dashboard.charts import regime_scatter, btc_regime_bars, funding_vs_pnl
from dashboard.theme import COLORS


def layout(df: pd.DataFrame):
    if df.empty:
        return html.Div("No closed trades.", style={"color": COLORS["text_muted"], "padding": "40px"})

    return html.Div([
        # BTC Regime
        html.Div(style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}, children=[
            html.Div(style={"flex": "1", "minWidth": "450px"}, children=[
                dcc.Graph(figure=btc_regime_bars(df), config={"displayModeBar": False}),
            ]),
            html.Div(style={"flex": "1", "minWidth": "450px"}, children=[
                dcc.Graph(figure=funding_vs_pnl(df), config={"displayModeBar": False}),
            ]),
        ]),

        # Engine state at entry vs PnL
        html.Div(style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}, children=[
            html.Div(style={"flex": "1", "minWidth": "400px"}, children=[
                dcc.Graph(figure=regime_scatter(df, "hurst", "Hurst"), config={"displayModeBar": False}),
            ]),
            html.Div(style={"flex": "1", "minWidth": "400px"}, children=[
                dcc.Graph(figure=regime_scatter(df, "volatility", "Volatility"), config={"displayModeBar": False}),
            ]),
        ]),

        html.Div(style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}, children=[
            html.Div(style={"flex": "1", "minWidth": "400px"}, children=[
                dcc.Graph(figure=regime_scatter(df, "z_score", "Z-Score"), config={"displayModeBar": False}),
            ]),
            html.Div(style={"flex": "1", "minWidth": "400px"}, children=[
                dcc.Graph(figure=regime_scatter(df, "drift", "Drift"), config={"displayModeBar": False}),
            ]),
        ]),
    ])
