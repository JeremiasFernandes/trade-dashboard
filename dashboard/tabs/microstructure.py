from dash import html, dcc
import pandas as pd
from dashboard.charts import (
    microstructure_scatter, cvd_divergence_winrate, delta_exhaustion_impact,
)
from dashboard.theme import COLORS


def layout(df: pd.DataFrame):
    if df.empty:
        return html.Div("No closed trades.", style={"color": COLORS["text_muted"], "padding": "40px"})

    return html.Div([
        # OFI & VPIN scatter plots
        html.Div(style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}, children=[
            html.Div(style={"flex": "1", "minWidth": "450px"}, children=[
                dcc.Graph(
                    figure=microstructure_scatter(df, "ofi_at_entry", "LOG-OFI"),
                    config={"displayModeBar": False},
                ),
            ]),
            html.Div(style={"flex": "1", "minWidth": "450px"}, children=[
                dcc.Graph(
                    figure=microstructure_scatter(df, "vpin_at_entry", "VPIN"),
                    config={"displayModeBar": False},
                ),
            ]),
        ]),

        # CVD divergence & delta exhaustion
        html.Div(style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}, children=[
            html.Div(style={"flex": "1", "minWidth": "450px"}, children=[
                dcc.Graph(
                    figure=cvd_divergence_winrate(df),
                    config={"displayModeBar": False},
                ),
            ]),
            html.Div(style={"flex": "1", "minWidth": "450px"}, children=[
                dcc.Graph(
                    figure=delta_exhaustion_impact(df),
                    config={"displayModeBar": False},
                ),
            ]),
        ]),

        # CVD at entry scatter
        html.Div(style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}, children=[
            html.Div(style={"flex": "1", "minWidth": "450px"}, children=[
                dcc.Graph(
                    figure=microstructure_scatter(df, "cvd_at_entry", "CVD"),
                    config={"displayModeBar": False},
                ),
            ]),
            html.Div(style={"flex": "1", "minWidth": "450px"}, children=[
                dcc.Graph(
                    figure=microstructure_scatter(df, "candle_delta_at_entry", "Candle Delta"),
                    config={"displayModeBar": False},
                ),
            ]),
        ]),
    ])
