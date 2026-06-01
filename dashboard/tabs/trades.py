from dash import html
import dash_ag_grid as dag
import pandas as pd
from dashboard.theme import COLORS


PNL_CELL_STYLE = {
    "styleConditions": [
        {"condition": "params.value > 0", "style": {"color": COLORS["green"]}},
        {"condition": "params.value <= 0", "style": {"color": COLORS["red"]}},
    ]
}

ALL_COLUMNS = [
    "symbol", "direction_label", "strategy_type", "mode",
    "entry_time", "exit_time",
    "entry_price", "signal_price", "fill_price", "exit_price",
    "slippage", "size", "leverage", "risk_amount_usd",
    "sl_price", "sl_pct", "tp_price",
    "net_pnl", "gross_pnl", "costs", "r_multiple",
    "exit_reason", "tp_hit",
    "mfe_pct", "mae_pct", "exit_efficiency", "mfe_time_candles",
    "best_price", "worst_price",
    "duration_hours", "candles_in_trade",
    "z_score", "drift", "hurst", "volatility", "confidence_factor", "risk_mult",
    "z_score_at_exit", "drift_at_exit", "hurst_at_exit", "volatility_at_exit",
    "funding_rate", "open_interest", "btc_price",
    "funding_rate_at_exit", "btc_price_at_exit", "btc_return_during_trade",
    "drift_sign_age", "hurst_delta", "fib_step",
    "ofi_at_entry", "cvd_at_entry", "candle_delta_at_entry", "vpin_at_entry", "cvd_divergence",
    "ofi_at_exit", "cvd_at_exit", "vpin_at_exit", "delta_exhaustion_at_exit",
]

COLUMN_DEFS = [
    # Core
    {"field": "symbol", "headerName": "Symbol", "width": 100, "pinned": "left"},
    {"field": "direction_label", "headerName": "Dir", "width": 70},
    {"field": "strategy_type", "headerName": "Strat", "width": 80},
    {"field": "mode", "headerName": "Mode", "width": 70, "hide": True},
    # Time
    {"field": "entry_time", "headerName": "Entry Time", "width": 140},
    {"field": "exit_time", "headerName": "Exit Time", "width": 140},
    # Prices
    {"field": "entry_price", "headerName": "Entry $", "width": 110, "type": "numericColumn"},
    {"field": "signal_price", "headerName": "Signal $", "width": 110, "type": "numericColumn", "hide": True},
    {"field": "fill_price", "headerName": "Fill $", "width": 110, "type": "numericColumn", "hide": True},
    {"field": "exit_price", "headerName": "Exit $", "width": 110, "type": "numericColumn"},
    {"field": "slippage", "headerName": "Slip", "width": 75, "type": "numericColumn"},
    # Sizing
    {"field": "size", "headerName": "Size", "width": 90, "type": "numericColumn"},
    {"field": "leverage", "headerName": "Lev", "width": 65, "type": "numericColumn"},
    {"field": "risk_amount_usd", "headerName": "Risk$", "width": 85, "type": "numericColumn"},
    # Risk
    {"field": "sl_price", "headerName": "SL $", "width": 100, "type": "numericColumn", "hide": True},
    {"field": "sl_pct", "headerName": "SL%", "width": 70, "type": "numericColumn"},
    {"field": "tp_price", "headerName": "TP $", "width": 100, "type": "numericColumn", "hide": True},
    # PnL
    {"field": "net_pnl", "headerName": "PnL", "width": 100, "type": "numericColumn", "cellStyle": PNL_CELL_STYLE},
    {"field": "gross_pnl", "headerName": "Gross", "width": 90, "type": "numericColumn", "hide": True, "cellStyle": PNL_CELL_STYLE},
    {"field": "costs", "headerName": "Costs", "width": 70, "type": "numericColumn", "hide": True},
    {"field": "r_multiple", "headerName": "R", "width": 65, "type": "numericColumn", "cellStyle": PNL_CELL_STYLE},
    {"field": "exit_reason", "headerName": "Reason", "width": 120},
    {"field": "tp_hit", "headerName": "TP?", "width": 60},
    # MFE/MAE
    {"field": "mfe_pct", "headerName": "MFE%", "width": 75, "type": "numericColumn"},
    {"field": "mae_pct", "headerName": "MAE%", "width": 75, "type": "numericColumn"},
    {"field": "exit_efficiency", "headerName": "Eff%", "width": 70, "type": "numericColumn"},
    {"field": "mfe_time_candles", "headerName": "MFE@", "width": 65, "type": "numericColumn", "hide": True},
    {"field": "best_price", "headerName": "Best $", "width": 100, "type": "numericColumn", "hide": True},
    {"field": "worst_price", "headerName": "Worst $", "width": 100, "type": "numericColumn", "hide": True},
    # Duration
    {"field": "duration_hours", "headerName": "Hrs", "width": 65, "type": "numericColumn"},
    {"field": "candles_in_trade", "headerName": "Candles", "width": 75, "type": "numericColumn", "hide": True},
    # Engine state entry
    {"field": "z_score", "headerName": "Z", "width": 70, "type": "numericColumn"},
    {"field": "drift", "headerName": "Drift", "width": 80, "type": "numericColumn", "hide": True},
    {"field": "hurst", "headerName": "Hurst", "width": 70, "type": "numericColumn"},
    {"field": "volatility", "headerName": "Vol%", "width": 70, "type": "numericColumn"},
    {"field": "confidence_factor", "headerName": "Conf", "width": 65, "type": "numericColumn", "hide": True},
    {"field": "risk_mult", "headerName": "RiskM", "width": 70, "type": "numericColumn", "hide": True},
    # Engine state exit
    {"field": "z_score_at_exit", "headerName": "Z Exit", "width": 75, "type": "numericColumn", "hide": True},
    {"field": "drift_at_exit", "headerName": "Drift Exit", "width": 90, "type": "numericColumn", "hide": True},
    {"field": "hurst_at_exit", "headerName": "Hurst Exit", "width": 85, "type": "numericColumn", "hide": True},
    {"field": "volatility_at_exit", "headerName": "Vol% Exit", "width": 85, "type": "numericColumn", "hide": True},
    # Market data entry
    {"field": "funding_rate", "headerName": "Fund", "width": 80, "type": "numericColumn", "hide": True},
    {"field": "open_interest", "headerName": "OI", "width": 90, "type": "numericColumn", "hide": True},
    {"field": "btc_price", "headerName": "BTC$", "width": 100, "type": "numericColumn", "hide": True},
    # Market data exit
    {"field": "funding_rate_at_exit", "headerName": "Fund Exit", "width": 90, "type": "numericColumn", "hide": True},
    {"field": "btc_price_at_exit", "headerName": "BTC$ Exit", "width": 100, "type": "numericColumn", "hide": True},
    {"field": "btc_return_during_trade", "headerName": "BTC Ret%", "width": 90, "type": "numericColumn", "hide": True},
    # Regime
    {"field": "drift_sign_age", "headerName": "DriftAge", "width": 80, "type": "numericColumn", "hide": True},
    {"field": "hurst_delta", "headerName": "H Delta", "width": 80, "type": "numericColumn", "hide": True},
    {"field": "fib_step", "headerName": "Fib", "width": 55, "type": "numericColumn", "hide": True},
    # Microstructure entry
    {"field": "ofi_at_entry", "headerName": "OFI In", "width": 80, "type": "numericColumn", "hide": True},
    {"field": "cvd_at_entry", "headerName": "CVD In", "width": 80, "type": "numericColumn", "hide": True},
    {"field": "candle_delta_at_entry", "headerName": "CDelta In", "width": 85, "type": "numericColumn", "hide": True},
    {"field": "vpin_at_entry", "headerName": "VPIN In", "width": 80, "type": "numericColumn", "hide": True},
    {"field": "cvd_divergence", "headerName": "CVD Div", "width": 85, "hide": True},
    # Microstructure exit
    {"field": "ofi_at_exit", "headerName": "OFI Out", "width": 80, "type": "numericColumn", "hide": True},
    {"field": "cvd_at_exit", "headerName": "CVD Out", "width": 80, "type": "numericColumn", "hide": True},
    {"field": "vpin_at_exit", "headerName": "VPIN Out", "width": 80, "type": "numericColumn", "hide": True},
    {"field": "delta_exhaustion_at_exit", "headerName": "DExhaust", "width": 80, "hide": True},
]


def _build_csv_href(date_range: dict | None) -> str:
    base = "/trades/export/csv"
    params = []
    if date_range:
        if date_range.get("start"):
            params.append(f"start_date={date_range['start']}")
        if date_range.get("end"):
            params.append(f"end_date={date_range['end']}")
    if params:
        return f"{base}?{'&'.join(params)}"
    return base


def layout(df: pd.DataFrame, date_range: dict | None = None):
    if df.empty:
        return html.Div("No closed trades yet.", style={"color": COLORS["text_muted"], "padding": "40px"})

    available = [c for c in ALL_COLUMNS if c in df.columns]
    display_df = df[available].copy()

    if "entry_time" in display_df:
        display_df["entry_time"] = display_df["entry_time"].dt.strftime("%Y-%m-%d %H:%M")
    if "exit_time" in display_df:
        display_df["exit_time"] = display_df["exit_time"].dt.strftime("%Y-%m-%d %H:%M")

    for col in ["mfe_pct", "mae_pct"]:
        if col in display_df:
            display_df[col] = (display_df[col] * 100).round(3)
    if "exit_efficiency" in display_df:
        display_df["exit_efficiency"] = (display_df["exit_efficiency"] * 100).round(1)
    for col in ["net_pnl", "gross_pnl"]:
        if col in display_df:
            display_df[col] = display_df[col].round(4)
    if "r_multiple" in display_df:
        display_df["r_multiple"] = display_df["r_multiple"].round(2)
    if "leverage" in display_df:
        display_df["leverage"] = display_df["leverage"].round(1)
    if "z_score" in display_df:
        display_df["z_score"] = display_df["z_score"].round(3)
    for col in ["volatility", "volatility_at_exit", "btc_return_during_trade"]:
        if col in display_df:
            display_df[col] = (display_df[col] * 100).round(3)
    if "duration_hours" in display_df:
        display_df["duration_hours"] = display_df["duration_hours"].round(1)
    if "slippage" in display_df:
        display_df["slippage"] = display_df["slippage"].round(6)
    for col in ["hurst", "hurst_at_exit", "hurst_delta", "confidence_factor"]:
        if col in display_df:
            display_df[col] = display_df[col].round(3)
    if "risk_amount_usd" in display_df:
        display_df["risk_amount_usd"] = display_df["risk_amount_usd"].round(2)

    display_df = display_df.sort_values("entry_time", ascending=False)

    active_defs = [d for d in COLUMN_DEFS if d["field"] in available]

    csv_href = _build_csv_href(date_range)

    return html.Div([
        html.Div(
            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "12px"},
            children=[
                html.Div(
                    f"{len(display_df)} closed trades — right-click column header to show/hide columns",
                    style={"color": COLORS["text_muted"], "fontSize": "13px"},
                ),
                html.A(
                    "Export CSV",
                    href=csv_href,
                    target="_blank",
                    style={
                        "backgroundColor": COLORS["border"],
                        "color": COLORS["text"],
                        "border": "none",
                        "borderRadius": "6px",
                        "padding": "6px 16px",
                        "fontSize": "12px",
                        "textDecoration": "none",
                        "cursor": "pointer",
                    },
                ),
            ],
        ),
        dag.AgGrid(
            id="trades-grid",
            rowData=display_df.to_dict("records"),
            columnDefs=active_defs,
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
