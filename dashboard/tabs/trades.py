from dash import html
import dash_ag_grid as dag
import pandas as pd
from dashboard.theme import COLORS


def layout(df: pd.DataFrame):
    if df.empty:
        return html.Div("No closed trades yet.", style={"color": COLORS["text_muted"], "padding": "40px"})

    display_df = df[[
        "symbol", "direction_label", "strategy_type", "entry_time", "exit_time",
        "entry_price", "exit_price", "size", "leverage",
        "net_pnl", "r_multiple", "exit_reason",
        "mfe_pct", "mae_pct", "exit_efficiency",
        "z_score", "volatility", "duration_hours",
    ]].copy()

    display_df["entry_time"] = display_df["entry_time"].dt.strftime("%Y-%m-%d %H:%M")
    display_df["exit_time"] = display_df["exit_time"].dt.strftime("%Y-%m-%d %H:%M")
    display_df["mfe_pct"] = (display_df["mfe_pct"] * 100).round(3)
    display_df["mae_pct"] = (display_df["mae_pct"] * 100).round(3)
    display_df["exit_efficiency"] = (display_df["exit_efficiency"] * 100).round(1)
    display_df["net_pnl"] = display_df["net_pnl"].round(4)
    display_df["r_multiple"] = display_df["r_multiple"].round(2)
    display_df["leverage"] = display_df["leverage"].round(1)
    display_df["z_score"] = display_df["z_score"].round(3)
    display_df["volatility"] = (display_df["volatility"] * 100).round(3)
    display_df["duration_hours"] = display_df["duration_hours"].round(1)

    display_df = display_df.sort_values("entry_time", ascending=False)

    column_defs = [
        {"field": "symbol", "headerName": "Symbol", "width": 100, "pinned": "left"},
        {"field": "direction_label", "headerName": "Dir", "width": 70},
        {"field": "strategy_type", "headerName": "Strategy", "width": 90},
        {"field": "entry_time", "headerName": "Entry", "width": 140},
        {"field": "exit_time", "headerName": "Exit", "width": 140},
        {"field": "entry_price", "headerName": "Entry $", "width": 110, "type": "numericColumn"},
        {"field": "exit_price", "headerName": "Exit $", "width": 110, "type": "numericColumn"},
        {"field": "size", "headerName": "Size", "width": 90, "type": "numericColumn"},
        {"field": "leverage", "headerName": "Lev", "width": 65, "type": "numericColumn"},
        {
            "field": "net_pnl", "headerName": "PnL", "width": 100, "type": "numericColumn",
            "cellStyle": {
                "styleConditions": [
                    {"condition": "params.value > 0", "style": {"color": COLORS["green"]}},
                    {"condition": "params.value <= 0", "style": {"color": COLORS["red"]}},
                ]
            },
        },
        {
            "field": "r_multiple", "headerName": "R", "width": 65, "type": "numericColumn",
            "cellStyle": {
                "styleConditions": [
                    {"condition": "params.value > 0", "style": {"color": COLORS["green"]}},
                    {"condition": "params.value <= 0", "style": {"color": COLORS["red"]}},
                ]
            },
        },
        {"field": "exit_reason", "headerName": "Reason", "width": 120},
        {"field": "mfe_pct", "headerName": "MFE%", "width": 75, "type": "numericColumn"},
        {"field": "mae_pct", "headerName": "MAE%", "width": 75, "type": "numericColumn"},
        {"field": "exit_efficiency", "headerName": "Eff%", "width": 70, "type": "numericColumn"},
        {"field": "z_score", "headerName": "Z", "width": 70, "type": "numericColumn"},
        {"field": "volatility", "headerName": "Vol%", "width": 70, "type": "numericColumn"},
        {"field": "duration_hours", "headerName": "Hrs", "width": 65, "type": "numericColumn"},
    ]

    return html.Div([
        html.Div(
            f"{len(display_df)} closed trades",
            style={"color": COLORS["text_muted"], "marginBottom": "12px", "fontSize": "13px"},
        ),
        dag.AgGrid(
            id="trades-grid",
            rowData=display_df.to_dict("records"),
            columnDefs=column_defs,
            defaultColDef={
                "sortable": True,
                "filter": True,
                "resizable": True,
                "floatingFilter": True,
            },
            dashGridOptions={
                "pagination": True,
                "paginationPageSize": 50,
                "animateRows": True,
                "rowSelection": "single",
            },
            style={
                "height": "calc(100vh - 200px)",
                "width": "100%",
            },
            className="ag-theme-alpine-dark",
        ),
    ])
