# Add these to your existing schemas.py file

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

# MT5 Connection schemas (updated)
class MT5ConnectionCreate(BaseModel):
    login: int
    password: str
    server: str
    broker: str
    account_type: str  # REAL/DEMO

class MT5ConnectionOut(BaseModel):
    id: int
    broker: str
    account_type: str
    is_active: bool
    last_connection: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MT5AccountInfo(BaseModel):
    login: int
    name: str
    server: str
    currency: str
    balance: float
    equity: float
    profit: float
    margin: float
    free_margin: float
    margin_level: float
    trade_allowed: bool
    trade_expert: bool

class MT5RatesRequest(BaseModel):
    symbol: str
    timeframe: str = "H1"  # M1, M5, H1, D1
    count: int = 100
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class MT5Rate(BaseModel):
    time: datetime
    open: float
    high: float
    low: float
    close: float
    tick_volume: int
    spread: int
    real_volume: int

class MT5RatesResponse(BaseModel):
    symbol: str
    timeframe: str
    count: int
    rates: List[MT5Rate]

class MT5Position(BaseModel):
    ticket: int
    symbol: str
    type: int
    volume: float
    price_open: float
    price_current: float
    profit: float
    swap: float
    comment: str
    time: datetime

class MT5StatusResponse(BaseModel):
    status: str
    bridge_connected: bool
    account_info: Optional[MT5AccountInfo] = None
    positions: Optional[List[MT5Position]] = None
    last_update: datetime
