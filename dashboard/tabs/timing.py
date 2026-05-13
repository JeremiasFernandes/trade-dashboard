from dash import html, dcc
import pandas as pd
from dashboard.charts import monthly_heatmap, day_of_week_performance, hour_of_day_performance, duration_vs_pnl
from dashboard.theme import COLORS


def layout(df: pd.DataFrame):
    if df.empty:
        return html.Div("No closed trades.", style={"color": COLORS["text_muted"], "padding": "40px"})

    return html.Div([
        dcc.Graph(figure=monthly_heatmap(df), config={"displayModeBar": False}),

        html.Div(style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}, children=[
            html.Div(style={"flex": "1", "minWidth": "400px"}, children=[
                dcc.Graph(figure=day_of_week_performance(df), config={"displayModeBar": False}),
            ]),
            html.Div(style={"flex": "1", "minWidth": "400px"}, children=[
                dcc.Graph(figure=hour_of_day_performance(df), config={"displayModeBar": False}),
            ]),
        ]),

        dcc.Graph(figure=duration_vs_pnl(df), config={"displayModeBar": False}),
    ])
