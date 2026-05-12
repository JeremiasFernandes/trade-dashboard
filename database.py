"""
Trade Analytics — aiosqlite backend
"""

import uuid
import aiosqlite
from datetime import datetime
from typing import List, Optional, Dict, Any

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS trades (
    trade_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    direction INTEGER NOT NULL,
    strategy_type TEXT NOT NULL,
    mode TEXT NOT NULL DEFAULT 'live',

    -- Entry prices
    entry_price REAL NOT NULL,
    signal_price REAL DEFAULT 0,
    fill_price REAL DEFAULT 0,
    slippage REAL DEFAULT 0,

    -- Sizing
    size REAL DEFAULT 0,
    leverage REAL DEFAULT 0,
    risk_amount_usd REAL DEFAULT 0,

    -- Risk
    sl_price REAL DEFAULT 0,
    sl_pct REAL DEFAULT 0,
    tp_price REAL DEFAULT 0,

    -- Engine state at entry
    z_score REAL DEFAULT 0,
    drift REAL DEFAULT 0,
    hurst REAL DEFAULT 0,
    volatility REAL DEFAULT 0,
    confidence_factor REAL DEFAULT 1,
    risk_mult REAL DEFAULT 1,

    -- Market data at entry
    funding_rate REAL DEFAULT 0,
    open_interest REAL DEFAULT 0,
    btc_price REAL DEFAULT 0,

    -- Regime duration
    drift_sign_age INTEGER DEFAULT 0,
    hurst_delta REAL DEFAULT 0,

    -- Pyramid
    fib_step INTEGER DEFAULT 1,

    entry_time TEXT,

    -- Exit fields (nullable)
    exit_price REAL,
    exit_reason TEXT,
    gross_pnl REAL,
    net_pnl REAL,
    costs REAL,
    r_multiple REAL,
    mfe_pct REAL,
    mae_pct REAL,
    exit_efficiency REAL,
    mfe_time_candles INTEGER,
    duration_seconds REAL,
    candles_in_trade INTEGER,
    best_price REAL,
    worst_price REAL,
    tp_hit INTEGER,
    z_score_at_exit REAL,
    drift_at_exit REAL,
    hurst_at_exit REAL,
    volatility_at_exit REAL,
    funding_rate_at_exit REAL,
    btc_price_at_exit REAL,
    btc_return_during_trade REAL,
    exit_time TEXT
);
"""

CREATE_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_strategy ON trades(strategy_type);
CREATE INDEX IF NOT EXISTS idx_trades_entry_time ON trades(entry_time);
CREATE INDEX IF NOT EXISTS idx_trades_exit_reason ON trades(exit_reason);
"""


class AnalyticsDatabase:
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self._db: Optional[aiosqlite.Connection] = None

    async def initialize(self):
        self._db = await aiosqlite.connect(self.db_path)
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(CREATE_TABLE)
        await self._db.executescript(CREATE_INDEXES)
        await self._db.commit()

    async def close(self):
        if self._db:
            await self._db.close()

    async def insert_entry(self, data: Dict[str, Any]) -> str:
        trade_id = str(uuid.uuid4())
        entry_time = data.get("entry_time") or datetime.utcnow().isoformat()
        if hasattr(entry_time, 'isoformat'):
            entry_time = entry_time.isoformat()

        await self._db.execute(
            """INSERT INTO trades (
                trade_id, symbol, direction, strategy_type, mode,
                entry_price, signal_price, fill_price, slippage,
                size, leverage, risk_amount_usd,
                sl_price, sl_pct, tp_price,
                z_score, drift, hurst, volatility, confidence_factor, risk_mult,
                funding_rate, open_interest, btc_price,
                drift_sign_age, hurst_delta, fib_step, entry_time
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?
            )""",
            (
                trade_id, data["symbol"], data["direction"], data["strategy_type"], data.get("mode", "live"),
                data["entry_price"], data.get("signal_price", 0), data.get("fill_price", 0), data.get("slippage", 0),
                data.get("size", 0), data.get("leverage", 0), data.get("risk_amount_usd", 0),
                data.get("sl_price", 0), data.get("sl_pct", 0), data.get("tp_price", 0),
                data.get("z_score", 0), data.get("drift", 0), data.get("hurst", 0),
                data.get("volatility", 0), data.get("confidence_factor", 1), data.get("risk_mult", 1),
                data.get("funding_rate", 0), data.get("open_interest", 0), data.get("btc_price", 0),
                data.get("drift_sign_age", 0), data.get("hurst_delta", 0), data.get("fib_step", 1),
                entry_time,
            )
        )
        await self._db.commit()
        return trade_id

    async def update_exit(self, trade_id: str, data: Dict[str, Any]) -> bool:
        exit_time = data.get("exit_time") or datetime.utcnow().isoformat()
        if hasattr(exit_time, 'isoformat'):
            exit_time = exit_time.isoformat()

        result = await self._db.execute(
            """UPDATE trades SET
                exit_price = ?, exit_reason = ?,
                gross_pnl = ?, net_pnl = ?, costs = ?, r_multiple = ?,
                mfe_pct = ?, mae_pct = ?, exit_efficiency = ?, mfe_time_candles = ?,
                duration_seconds = ?, candles_in_trade = ?,
                best_price = ?, worst_price = ?, tp_hit = ?,
                z_score_at_exit = ?, drift_at_exit = ?,
                hurst_at_exit = ?, volatility_at_exit = ?,
                funding_rate_at_exit = ?, btc_price_at_exit = ?,
                btc_return_during_trade = ?, exit_time = ?
            WHERE trade_id = ?""",
            (
                data["exit_price"], data["exit_reason"],
                data.get("gross_pnl", 0), data.get("net_pnl", 0),
                data.get("costs", 0), data.get("r_multiple", 0),
                data.get("mfe_pct", 0), data.get("mae_pct", 0),
                data.get("exit_efficiency", 0), data.get("mfe_time_candles", 0),
                data.get("duration_seconds", 0), data.get("candles_in_trade", 0),
                data.get("best_price", 0), data.get("worst_price", 0),
                1 if data.get("tp_hit") else 0,
                data.get("z_score_at_exit", 0), data.get("drift_at_exit", 0),
                data.get("hurst_at_exit", 0), data.get("volatility_at_exit", 0),
                data.get("funding_rate_at_exit", 0), data.get("btc_price_at_exit", 0),
                data.get("btc_return_during_trade", 0), exit_time,
                trade_id,
            )
        )
        await self._db.commit()
        return result.rowcount > 0

    async def get_trades(
        self,
        symbol: Optional[str] = None,
        strategy_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        closed_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        conditions = []
        params = []

        if symbol:
            conditions.append("symbol = ?")
            params.append(symbol)
        if strategy_type:
            conditions.append("strategy_type = ?")
            params.append(strategy_type)
        if start_date:
            conditions.append("entry_time >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("entry_time <= ?")
            params.append(end_date)
        if closed_only:
            conditions.append("exit_time IS NOT NULL")

        where = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"SELECT * FROM trades{where} ORDER BY entry_time DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = await self._db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def get_trade(self, trade_id: str) -> Optional[Dict[str, Any]]:
        cursor = await self._db.execute("SELECT * FROM trades WHERE trade_id = ?", (trade_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def get_stats(
        self,
        strategy_type: Optional[str] = None,
        hours: Optional[int] = None,
    ) -> Dict[str, Any]:
        conditions = ["exit_time IS NOT NULL"]
        params = []

        if strategy_type:
            conditions.append("strategy_type = ?")
            params.append(strategy_type)
        if hours:
            conditions.append("entry_time >= datetime('now', ?)")
            params.append(f"-{hours} hours")

        where = " WHERE " + " AND ".join(conditions)

        cursor = await self._db.execute(
            f"""SELECT
                COUNT(*) as total_trades,
                SUM(CASE WHEN net_pnl > 0 THEN 1 ELSE 0 END) as winners,
                SUM(CASE WHEN net_pnl <= 0 THEN 1 ELSE 0 END) as losers,
                SUM(net_pnl) as total_pnl,
                AVG(net_pnl) as avg_pnl,
                AVG(CASE WHEN net_pnl > 0 THEN net_pnl END) as avg_win,
                AVG(CASE WHEN net_pnl <= 0 THEN net_pnl END) as avg_loss,
                AVG(r_multiple) as avg_r_multiple,
                AVG(mfe_pct) as avg_mfe,
                AVG(mae_pct) as avg_mae,
                AVG(exit_efficiency) as avg_exit_efficiency,
                AVG(duration_seconds) as avg_duration
            FROM trades{where}""",
            params,
        )
        row = await cursor.fetchone()
        if not row:
            return {}

        d = dict(row)
        total = d.get("total_trades", 0) or 0
        winners = d.get("winners", 0) or 0
        d["win_rate"] = (winners / total * 100) if total > 0 else 0
        return d
