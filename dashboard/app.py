"""
Dashboard Dash — montado sobre Flask, integrado ao FastAPI via WSGIMiddleware.
"""

import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

from dashboard import theme  # noqa: F401 — registra template plotly
from dashboard.data import load_closed_trades
from dashboard.tabs import overview, trades, mfe_mae, strategy, regime, timing, microstructure
from dashboard.theme import COLORS


def create_dash_app() -> dash.Dash:
    app = dash.Dash(
        __name__,
        requests_pathname_prefix="/dashboard/",
        external_stylesheets=[
            dbc.themes.DARKLY,
            "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
        ],
        suppress_callback_exceptions=True,
    )

    app.title = "Trade Analytics"

    TABS = [
        {"id": "overview", "label": "Overview"},
        {"id": "trades", "label": "Trade Log"},
        {"id": "mfe_mae", "label": "MFE / MAE"},
        {"id": "strategy", "label": "Strategy"},
        {"id": "regime", "label": "Regime"},
        {"id": "microstructure", "label": "Microstructure"},
        {"id": "timing", "label": "Timing"},
    ]

    app.layout = html.Div(
        style={
            "backgroundColor": COLORS["bg"],
            "minHeight": "100vh",
            "fontFamily": "Inter, -apple-system, sans-serif",
            "color": COLORS["text"],
        },
        children=[
            # Header
            html.Div(
                style={
                    "backgroundColor": COLORS["card"],
                    "borderBottom": f"1px solid {COLORS['border']}",
                    "padding": "12px 24px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                },
                children=[
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "12px"},
                        children=[
                            html.H1(
                                "Trade Analytics",
                                style={"fontSize": "18px", "fontWeight": "700", "margin": "0"},
                            ),
                            html.Span(
                                id="trade-count-badge",
                                style={
                                    "backgroundColor": COLORS["blue"],
                                    "color": "#fff",
                                    "borderRadius": "12px",
                                    "padding": "2px 10px",
                                    "fontSize": "11px",
                                    "fontWeight": "600",
                                },
                            ),
                        ],
                    ),
                    html.Button(
                        "Refresh",
                        id="refresh-btn",
                        n_clicks=0,
                        style={
                            "backgroundColor": COLORS["border"],
                            "color": COLORS["text"],
                            "border": "none",
                            "borderRadius": "6px",
                            "padding": "6px 16px",
                            "fontSize": "12px",
                            "cursor": "pointer",
                        },
                    ),
                ],
            ),

            # Tabs
            html.Div(
                style={
                    "backgroundColor": COLORS["card"],
                    "borderBottom": f"1px solid {COLORS['border']}",
                    "padding": "0 24px",
                },
                children=[
                    dcc.Tabs(
                        id="main-tabs",
                        value="overview",
                        children=[
                            dcc.Tab(
                                label=t["label"],
                                value=t["id"],
                                style={
                                    "backgroundColor": "transparent",
                                    "border": "none",
                                    "color": COLORS["text_muted"],
                                    "padding": "10px 16px",
                                    "fontSize": "13px",
                                },
                                selected_style={
                                    "backgroundColor": "transparent",
                                    "border": "none",
                                    "borderBottom": f"2px solid {COLORS['blue']}",
                                    "color": COLORS["text"],
                                    "padding": "10px 16px",
                                    "fontSize": "13px",
                                    "fontWeight": "600",
                                },
                            )
                            for t in TABS
                        ],
                        style={"height": "auto"},
                    ),
                ],
            ),

            # Content
            html.Div(
                id="tab-content",
                style={"padding": "20px 24px"},
            ),

            # Hidden store for data refresh
            dcc.Store(id="data-store"),
        ],
    )

    @app.callback(
        Output("tab-content", "children"),
        Output("trade-count-badge", "children"),
        Input("main-tabs", "value"),
        Input("refresh-btn", "n_clicks"),
    )
    def render_tab(tab_id, _n_clicks):
        df = load_closed_trades()
        count_text = f"{len(df)} trades"

        TAB_RENDERERS = {
            "overview": overview.layout,
            "trades": trades.layout,
            "mfe_mae": mfe_mae.layout,
            "strategy": strategy.layout,
            "regime": regime.layout,
            "microstructure": microstructure.layout,
            "timing": timing.layout,
        }

        renderer = TAB_RENDERERS.get(tab_id, overview.layout)
        return renderer(df), count_text

    return app
