from dash import html, dcc
import pandas as pd
from dashboard.data import compute_equity_curve, compute_stats
from dashboard.kpi import kpi_card, kpi_row
from dashboard.charts import equity_curve, drawdown_chart, pnl_distribution, r_multiple_distribution, win_rate_rolling, cumulative_r
from dashboard.theme import COLORS


def layout(df: pd.DataFrame):
    stats = compute_stats(df)
    eq = compute_equity_curve(df)

    return html.Div([
        # KPI Row 1
        kpi_row([
            kpi_card("Total PnL", stats["total_pnl"], prefix="$",
                     subtitle=f"{stats['total_trades']} trades"),
            kpi_card("Win Rate", stats["win_rate"], suffix="%",
                     color=COLORS["green"] if stats["win_rate"] >= 50 else COLORS["red"],
                     subtitle=f"{stats['winners']}W / {stats['losers']}L"),
            kpi_card("Profit Factor", stats["profit_factor"],
                     color=COLORS["green"] if stats["profit_factor"] >= 1.5 else COLORS["orange"]),
            kpi_card("Avg R-Multiple", stats["avg_r_multiple"], suffix="R",
                     subtitle=f"Expectancy: {stats['expectancy']:.4f}"),
            kpi_card("Max Drawdown", stats["max_drawdown"], prefix="$"),
        ]),

        # KPI Row 2
        kpi_row([
            kpi_card("Avg Win", stats["avg_win"], prefix="$", color=COLORS["green"]),
            kpi_card("Avg Loss", stats["avg_loss"], prefix="$", color=COLORS["red"]),
            kpi_card("Avg Duration", f"{stats['avg_duration_h']}h", color=COLORS["text"]),
            kpi_card("Avg MFE", stats["avg_mfe"], suffix="%", color=COLORS["cyan"]),
            kpi_card("Avg MAE", stats["avg_mae"], suffix="%", color=COLORS["orange"]),
            kpi_card("Exit Efficiency", stats["avg_exit_efficiency"], suffix="%",
                     color=COLORS["green"] if stats["avg_exit_efficiency"] >= 50 else COLORS["orange"]),
        ]),

        # Charts row 1
        html.Div(style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}, children=[
            html.Div(style={"flex": "2", "minWidth": "500px"}, children=[
                dcc.Graph(figure=equity_curve(eq), config={"displayModeBar": False}),
            ]),
            html.Div(style={"flex": "1", "minWidth": "300px"}, children=[
                dcc.Graph(figure=pnl_distribution(df), config={"displayModeBar": False}),
            ]),
        ]),

        # Drawdown
        dcc.Graph(figure=drawdown_chart(eq), config={"displayModeBar": False}),

        # Charts row 2
        html.Div(style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}, children=[
            html.Div(style={"flex": "1", "minWidth": "300px"}, children=[
                dcc.Graph(figure=r_multiple_distribution(df), config={"displayModeBar": False}),
            ]),
            html.Div(style={"flex": "1", "minWidth": "300px"}, children=[
                dcc.Graph(figure=cumulative_r(df), config={"displayModeBar": False}),
            ]),
            html.Div(style={"flex": "1", "minWidth": "300px"}, children=[
                dcc.Graph(figure=win_rate_rolling(df), config={"displayModeBar": False}),
            ]),
        ]),
    ])
