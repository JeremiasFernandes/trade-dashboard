"""
Trade Analytics API — FastAPI service
======================================

Servico independente para registro e consulta de trades.
Executar: uvicorn api:app --host 0.0.0.0 --port 8100
"""

from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query

from models import (
    TradeEntryPayload, TradeExitPayload,
    TradeEntryResponse, TradeExitResponse,
)
from database import AnalyticsDatabase

db = AnalyticsDatabase()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.initialize()
    yield
    await db.close()


app = FastAPI(
    title="Trade Analytics API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post("/trades/entry", response_model=TradeEntryResponse)
async def register_entry(payload: TradeEntryPayload):
    trade_id = await db.insert_entry(payload.model_dump())
    return TradeEntryResponse(trade_id=trade_id)


@app.post("/trades/exit", response_model=TradeExitResponse)
async def register_exit(payload: TradeExitPayload):
    trade = await db.get_trade(payload.trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail=f"Trade {payload.trade_id} not found")

    success = await db.update_exit(payload.trade_id, payload.model_dump())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update trade")

    return TradeExitResponse(trade_id=payload.trade_id)


@app.get("/trades")
async def list_trades(
    symbol: Optional[str] = None,
    strategy_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    closed_only: bool = False,
    limit: int = Query(default=100, le=1000),
    offset: int = 0,
):
    trades = await db.get_trades(
        symbol=symbol,
        strategy_type=strategy_type,
        start_date=start_date,
        end_date=end_date,
        closed_only=closed_only,
        limit=limit,
        offset=offset,
    )
    return {"trades": trades, "count": len(trades)}


@app.get("/trades/{trade_id}")
async def get_trade(trade_id: str):
    trade = await db.get_trade(trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
    return trade


@app.get("/trades/stats/summary")
async def get_stats(
    strategy_type: Optional[str] = None,
    hours: Optional[int] = None,
):
    stats = await db.get_stats(strategy_type=strategy_type, hours=hours)
    return stats


@app.get("/health")
async def health():
    return {"status": "ok"}
