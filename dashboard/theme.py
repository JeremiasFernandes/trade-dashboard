import plotly.graph_objects as go
import plotly.io as pio

COLORS = {
    "bg": "#0d1117",
    "card": "#161b22",
    "border": "#30363d",
    "text": "#c9d1d9",
    "text_muted": "#8b949e",
    "green": "#3fb950",
    "red": "#f85149",
    "blue": "#58a6ff",
    "purple": "#bc8cff",
    "orange": "#d29922",
    "cyan": "#39d2c0",
    "yellow": "#e3b341",
    "pink": "#f778ba",
    "grid": "#21262d",
}

STRATEGY_COLORS = {
    "trend": COLORS["blue"],
    "mr": COLORS["purple"],
}

EXIT_REASON_COLORS = {
    "Trailing_Stop": COLORS["cyan"],
    "Stop_Loss": COLORS["red"],
    "Take_Profit": COLORS["green"],
    "Trend_Reversal": COLORS["orange"],
    "Mean_Reversion": COLORS["blue"],
}

PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font=dict(color=COLORS["text"], family="Inter, -apple-system, sans-serif", size=12),
        xaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"]),
        yaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"]),
        margin=dict(l=50, r=20, t=40, b=40),
        colorway=[
            COLORS["blue"], COLORS["green"], COLORS["purple"],
            COLORS["orange"], COLORS["cyan"], COLORS["pink"],
            COLORS["yellow"], COLORS["red"],
        ],
        hoverlabel=dict(
            bgcolor=COLORS["card"],
            bordercolor=COLORS["border"],
            font=dict(color=COLORS["text"]),
        ),
    )
)

pio.templates["analytics_dark"] = PLOTLY_TEMPLATE
pio.templates.default = "analytics_dark"
