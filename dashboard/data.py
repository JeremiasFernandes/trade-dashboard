"""
Data layer — leitura sincrona do SQLite para o dashboard Dash.
Retorna pandas DataFrames.
"""

import os
import sqlite3
import pandas as pd
import numpy as np

DB_PATH = os.environ.get("DB_PATH", "analytics.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_closed_trades() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM trades WHERE exit_time IS NOT NULL ORDER BY entry_time ASC",
        conn,
    )
    conn.close()

    if df.empty:
        return df

    df["entry_time"] = pd.to_datetime(df["entry_time"], errors="coerce")
    df["exit_time"] = pd.to_datetime(df["exit_time"], errors="coerce")
    df["direction_label"] = df["direction"].map({1: "LONG", -1: "SHORT"})
    df["is_winner"] = df["net_pnl"] > 0
    df["result_label"] = df["is_winner"].map({True: "Winner", False: "Loser"})
    df["duration_hours"] = df["duration_seconds"] / 3600
    df["tp_hit"] = df["tp_hit"].astype(bool)

    return df


def load_open_trades() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM trades WHERE exit_time IS NULL ORDER BY entry_time DESC",
        conn,
    )
    conn.close()
    if not df.empty:
        df["entry_time"] = pd.to_datetime(df["entry_time"], errors="coerce")
    return df


def compute_equity_curve(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["exit_time", "cumulative_pnl", "drawdown", "peak"])

    eq = df.sort_values("exit_time").copy()
    eq["cumulative_pnl"] = eq["net_pnl"].cumsum()
    eq["peak"] = eq["cumulative_pnl"].cummax()
    eq["drawdown"] = eq["cumulative_pnl"] - eq["peak"]
    eq["drawdown_pct"] = (eq["drawdown"] / eq["peak"].replace(0, np.nan)) * 100
    return eq


def compute_stats(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "total_trades": 0, "winners": 0, "losers": 0, "win_rate": 0,
            "total_pnl": 0, "avg_pnl": 0, "avg_win": 0, "avg_loss": 0,
            "profit_factor": 0, "max_drawdown": 0, "avg_r_multiple": 0,
            "expectancy": 0, "avg_duration_h": 0, "avg_mfe": 0, "avg_mae": 0,
            "avg_exit_efficiency": 0, "best_trade": 0, "worst_trade": 0,
            "avg_leverage": 0, "total_volume": 0,
        }

    winners = df[df["net_pnl"] > 0]
    losers = df[df["net_pnl"] <= 0]
    total_wins = winners["net_pnl"].sum()
    total_losses = abs(losers["net_pnl"].sum())

    eq = compute_equity_curve(df)
    max_dd = abs(eq["drawdown"].min()) if not eq.empty else 0

    win_rate = len(winners) / len(df) * 100 if len(df) > 0 else 0
    avg_win = winners["net_pnl"].mean() if len(winners) > 0 else 0
    avg_loss = losers["net_pnl"].mean() if len(losers) > 0 else 0
    pf = total_wins / total_losses if total_losses > 0 else float("inf")
    expectancy = (win_rate / 100 * avg_win) + ((1 - win_rate / 100) * avg_loss)

    return {
        "total_trades": len(df),
        "winners": len(winners),
        "losers": len(losers),
        "win_rate": round(win_rate, 1),
        "total_pnl": round(df["net_pnl"].sum(), 4),
        "avg_pnl": round(df["net_pnl"].mean(), 4),
        "avg_win": round(avg_win, 4),
        "avg_loss": round(avg_loss, 4),
        "profit_factor": round(pf, 2),
        "max_drawdown": round(max_dd, 4),
        "avg_r_multiple": round(df["r_multiple"].mean(), 2) if "r_multiple" in df else 0,
        "expectancy": round(expectancy, 4),
        "avg_duration_h": round(df["duration_hours"].mean(), 1) if "duration_hours" in df else 0,
        "avg_mfe": round(df["mfe_pct"].mean() * 100, 2) if "mfe_pct" in df else 0,
        "avg_mae": round(df["mae_pct"].mean() * 100, 2) if "mae_pct" in df else 0,
        "avg_exit_efficiency": round(df["exit_efficiency"].mean() * 100, 1) if "exit_efficiency" in df else 0,
        "best_trade": round(df["net_pnl"].max(), 4),
        "worst_trade": round(df["net_pnl"].min(), 4),
        "avg_leverage": round(df["leverage"].mean(), 1) if "leverage" in df else 0,
        "total_volume": round((df["size"] * df["entry_price"]).sum(), 2),
    }
