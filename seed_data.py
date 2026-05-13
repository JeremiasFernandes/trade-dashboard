"""
Gera trades sinteticos para popular o dashboard.
Uso standalone: python seed_data.py
Uso via API:    POST /seed?count=120
"""

import os
import sqlite3
import uuid
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any

SYMBOLS = ["BTC", "ETH", "SOL", "DOGE", "LINK", "AVAX", "ARB", "OP", "SUI", "PEPE"]
STRATEGIES = ["trend", "mr"]
EXIT_REASONS_TREND = ["Trailing_Stop", "Stop_Loss", "Trend_Reversal", "Take_Profit"]
EXIT_REASONS_MR = ["Take_Profit", "Stop_Loss", "Mean_Reversion"]

PRICES = {
    "BTC": 105000, "ETH": 3200, "SOL": 180, "DOGE": 0.18, "LINK": 18,
    "AVAX": 42, "ARB": 1.2, "OP": 2.5, "SUI": 3.8, "PEPE": 0.000015,
}


def generate_trade(i: int, base_time: datetime) -> Dict[str, Any]:
    symbol = random.choice(SYMBOLS)
    strategy = random.choice(STRATEGIES)
    direction = random.choice([1, -1])
    base_price = PRICES[symbol]
    entry_price = base_price * (1 + random.uniform(-0.03, 0.03))

    volatility = random.uniform(0.005, 0.04)
    sl_pct = np.clip(volatility * 2.5, 0.005, 0.10)
    risk_pct = random.choice([0.01, 0.01, 0.02, 0.03, 0.05])
    equity = 100
    risk_amount = equity * risk_pct
    sl_distance = entry_price * sl_pct
    size = risk_amount / sl_distance
    leverage = min((size * entry_price) / equity, 5.0)
    sl_price = entry_price * (1 - sl_pct) if direction == 1 else entry_price * (1 + sl_pct)

    z_score = random.uniform(1.5, 4.0) * (-1 if direction == 1 else 1)
    drift = random.uniform(-0.002, 0.002)
    hurst = random.uniform(0.35, 0.75)
    confidence = random.uniform(0.5, 1.0)
    funding_rate = random.uniform(-0.0003, 0.0003)
    btc_price = PRICES["BTC"] * (1 + random.uniform(-0.05, 0.05))
    drift_sign_age = random.randint(1, 30)
    hurst_delta = random.uniform(-0.1, 0.1)

    slippage = random.uniform(0.0001, 0.003)
    fill_price = entry_price * (1 + slippage * (1 if direction == 1 else -1))

    is_winner = random.random() < 0.48
    if is_winner:
        pnl_pct = random.uniform(0.005, 0.08)
        reasons = EXIT_REASONS_TREND if strategy == "trend" else EXIT_REASONS_MR
        exit_reason = random.choice([r for r in reasons if r != "Stop_Loss"])
    else:
        pnl_pct = -random.uniform(0.003, sl_pct)
        exit_reason = "Stop_Loss"

    exit_price = entry_price * (1 + pnl_pct) if direction == 1 else entry_price * (1 - pnl_pct)
    gross_pnl = (exit_price - entry_price) * size * direction
    costs = abs(size * entry_price * 0.0007)
    net_pnl = gross_pnl - costs
    r_multiple = net_pnl / risk_amount if risk_amount > 0 else 0

    if is_winner:
        mfe_pct = pnl_pct + random.uniform(0.002, 0.03)
        mae_pct = random.uniform(0.001, sl_pct * 0.5)
    else:
        mfe_pct = random.uniform(0.001, 0.02)
        mae_pct = abs(pnl_pct) + random.uniform(0, 0.01)

    exit_efficiency = (pnl_pct / mfe_pct) if mfe_pct > 0 else 0

    if direction == 1:
        best_price = entry_price * (1 + mfe_pct)
        worst_price = entry_price * (1 - mae_pct)
    else:
        best_price = entry_price * (1 - mfe_pct)
        worst_price = entry_price * (1 + mae_pct)

    entry_time = base_time + timedelta(hours=i * random.uniform(2, 12))
    duration_hours = random.uniform(0.5, 72)
    exit_time = entry_time + timedelta(hours=duration_hours)
    candles_in_trade = int(duration_hours) + 1
    mfe_time_candles = random.randint(1, max(1, candles_in_trade // 2))

    btc_return = random.uniform(-0.04, 0.04)
    btc_price_exit = btc_price * (1 + btc_return)
    tp_hit = 1 if exit_reason == "Take_Profit" else 0

    return {
        "trade_id": str(uuid.uuid4()),
        "symbol": symbol, "direction": direction,
        "strategy_type": strategy, "mode": "synthetic",
        "entry_price": entry_price, "signal_price": entry_price,
        "fill_price": fill_price, "slippage": slippage,
        "size": size, "leverage": leverage, "risk_amount_usd": risk_amount,
        "sl_price": sl_price, "sl_pct": sl_pct, "tp_price": 0,
        "z_score": z_score, "drift": drift, "hurst": hurst,
        "volatility": volatility, "confidence_factor": confidence, "risk_mult": 1.0,
        "funding_rate": funding_rate, "open_interest": random.uniform(1e6, 5e8),
        "btc_price": btc_price,
        "drift_sign_age": drift_sign_age, "hurst_delta": hurst_delta,
        "fib_step": random.choice([0, 1, 2]),
        "entry_time": entry_time.isoformat(),
        "exit_price": exit_price, "exit_reason": exit_reason,
        "gross_pnl": gross_pnl, "net_pnl": net_pnl, "costs": costs,
        "r_multiple": r_multiple,
        "mfe_pct": mfe_pct, "mae_pct": mae_pct,
        "exit_efficiency": exit_efficiency, "mfe_time_candles": mfe_time_candles,
        "duration_seconds": duration_hours * 3600, "candles_in_trade": candles_in_trade,
        "best_price": best_price, "worst_price": worst_price, "tp_hit": tp_hit,
        "z_score_at_exit": z_score * 0.5, "drift_at_exit": drift * 0.8,
        "hurst_at_exit": hurst + random.uniform(-0.05, 0.05),
        "volatility_at_exit": volatility * random.uniform(0.8, 1.2),
        "funding_rate_at_exit": funding_rate * random.uniform(0.5, 1.5),
        "btc_price_at_exit": btc_price_exit, "btc_return_during_trade": btc_return,
        "exit_time": exit_time.isoformat(),
    }


def generate_trades(count: int = 120) -> List[Dict[str, Any]]:
    base_time = datetime(2026, 3, 1, 8, 0)
    return [generate_trade(i, base_time) for i in range(count)]


def seed_to_sqlite(db_path: str, count: int = 120):
    conn = sqlite3.connect(db_path)

    cols = [
        "trade_id", "symbol", "direction", "strategy_type", "mode",
        "entry_price", "signal_price", "fill_price", "slippage",
        "size", "leverage", "risk_amount_usd",
        "sl_price", "sl_pct", "tp_price",
        "z_score", "drift", "hurst", "volatility", "confidence_factor", "risk_mult",
        "funding_rate", "open_interest", "btc_price",
        "drift_sign_age", "hurst_delta", "fib_step", "entry_time",
        "exit_price", "exit_reason", "gross_pnl", "net_pnl", "costs", "r_multiple",
        "mfe_pct", "mae_pct", "exit_efficiency", "mfe_time_candles",
        "duration_seconds", "candles_in_trade",
        "best_price", "worst_price", "tp_hit",
        "z_score_at_exit", "drift_at_exit", "hurst_at_exit", "volatility_at_exit",
        "funding_rate_at_exit", "btc_price_at_exit", "btc_return_during_trade",
        "exit_time",
    ]

    placeholders = ",".join(["?"] * len(cols))
    insert_sql = f"INSERT INTO trades ({','.join(cols)}) VALUES ({placeholders})"

    trades = generate_trades(count)
    rows = [tuple(t[c] for c in cols) for t in trades]
    conn.executemany(insert_sql, rows)
    conn.commit()
    conn.close()
    return len(trades)


if __name__ == "__main__":
    db_path = os.environ.get("DB_PATH", "analytics.db")
    from database import AnalyticsDatabase
    import asyncio

    async def init_and_seed():
        db = AnalyticsDatabase(db_path=db_path)
        await db.initialize()
        await db.close()
        n = seed_to_sqlite(db_path)
        print(f"Inserted {n} synthetic trades into {db_path}")

    asyncio.run(init_and_seed())
