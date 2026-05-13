"""
KPI card components.
"""

from dash import html
from .theme import COLORS


def kpi_card(title: str, value, subtitle: str = "", color: str = None, prefix: str = "", suffix: str = ""):
    if color is None:
        if isinstance(value, (int, float)) and value != 0:
            color = COLORS["green"] if value > 0 else COLORS["red"]
        else:
            color = COLORS["text"]

    return html.Div(
        style={
            "backgroundColor": COLORS["card"],
            "border": f"1px solid {COLORS['border']}",
            "borderRadius": "8px",
            "padding": "16px 20px",
            "minWidth": "160px",
            "flex": "1",
        },
        children=[
            html.Div(
                title,
                style={
                    "color": COLORS["text_muted"],
                    "fontSize": "11px",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.5px",
                    "marginBottom": "4px",
                },
            ),
            html.Div(
                f"{prefix}{value}{suffix}",
                style={
                    "color": color,
                    "fontSize": "24px",
                    "fontWeight": "600",
                    "lineHeight": "1.2",
                },
            ),
            html.Div(
                subtitle,
                style={
                    "color": COLORS["text_muted"],
                    "fontSize": "11px",
                    "marginTop": "4px",
                },
            ) if subtitle else None,
        ],
    )


def kpi_row(cards: list):
    return html.Div(
        style={
            "display": "flex",
            "gap": "12px",
            "flexWrap": "wrap",
            "marginBottom": "20px",
        },
        children=cards,
    )
