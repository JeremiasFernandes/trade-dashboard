"""
Trade Analytics — Pydantic Models
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TradeEntryPayload(BaseModel):
    symbol: str
    direction: int  # 1=long, -1=short
    strategy_type: str  # "trend" or "mr"
    mode: str = "live"  # "live" or "dryrun"

    # Precos
    entry_price: float
    signal_price: float
    fill_price: float
    slippage: float = 0.0

    # Sizing
    size: float
    leverage: float = 0.0
    risk_amount_usd: float = 0.0

    # Risk
    sl_price: float = 0.0
    sl_pct: float = 0.0
    tp_price: float = 0.0

    # Engine state at entry
    z_score: float = 0.0
    drift: float = 0.0
    hurst: float = 0.0
    volatility: float = 0.0
    confidence_factor: float = 1.0
    risk_mult: float = 1.0

    # Market data at entry
    funding_rate: float = 0.0
    open_interest: float = 0.0
    btc_price: float = 0.0

    # Regime duration (trend only)
    drift_sign_age: int = 0
    hurst_delta: float = 0.0

    # Pyramid
    fib_step: int = 1

    entry_time: Optional[datetime] = None


class TradeExitPayload(BaseModel):
    trade_id: str

    exit_price: float
    exit_reason: str

    # PnL
    gross_pnl: float = 0.0
    net_pnl: float = 0.0
    costs: float = 0.0
    r_multiple: float = 0.0

    # MFE/MAE
    mfe_pct: float = 0.0
    mae_pct: float = 0.0
    exit_efficiency: float = 0.0
    mfe_time_candles: int = 0

    # Duration
    duration_seconds: float = 0.0
    candles_in_trade: int = 0

    # Price extremes
    best_price: float = 0.0
    worst_price: float = 0.0
    tp_hit: bool = False

    # Engine state at exit
    z_score_at_exit: float = 0.0
    drift_at_exit: float = 0.0
    hurst_at_exit: float = 0.0
    volatility_at_exit: float = 0.0

    # Market data at exit
    funding_rate_at_exit: float = 0.0
    btc_price_at_exit: float = 0.0
    btc_return_during_trade: float = 0.0

    exit_time: Optional[datetime] = None


class TradeEntryResponse(BaseModel):
    trade_id: str
    status: str = "registered"


class TradeExitResponse(BaseModel):
    trade_id: str
    status: str = "updated"
