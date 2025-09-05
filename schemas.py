from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

# Enums matching database
class SignalTypeEnum(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class SignalOutcomeEnum(str, Enum):
    WIN = "WIN"
    LOSS = "LOSS"
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"

class SubscriptionStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"
    TRIAL = "TRIAL"

# User Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str  # Can be username or email
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    message: str
    user: UserOut

# Token Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None

# Subscription Schemas
class SubscriptionCreate(BaseModel):
    plan_name: str = "basic"
    payment_method: Optional[str] = None

class SubscriptionOut(BaseModel):
    id: int
    status: SubscriptionStatusEnum
    plan_name: str
    start_date: datetime
    end_date: Optional[datetime] = None
    auto_renew: bool

    class Config:
        from_attributes = True

# Signal Schemas
class SignalCreate(BaseModel):
    asset: str = Field(..., min_length=2, max_length=20)
    signal_type: SignalTypeEnum
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    is_public: bool = False

    @validator('asset')
    def validate_asset(cls, v):
        return v.upper().strip()

    @validator('stop_loss', 'take_profit')
    def validate_prices(cls, v, values, field):
        if v is not None and v <= 0:
            raise ValueError(f'{field.name} must be positive')
        return v

class SignalOut(BaseModel):
    id: int
    asset: str
    signal_type: SignalTypeEnum
    reliability: float
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    current_price: Optional[float] = None
    gemini_explanation: Optional[str] = None
    ml_confidence: Optional[float] = None
    market_conditions: Optional[Dict[str, Any]] = None
    price_action_score: Optional[float] = None
    volume_score: Optional[float] = None
    momentum_score: Optional[float] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_public: bool
    is_active: bool
    outcome: SignalOutcomeEnum
    profit_loss: float

    class Config:
        from_attributes = True

class SignalUpdate(BaseModel):
    outcome: Optional[SignalOutcomeEnum] = None
    profit_loss: Optional[float] = None
    is_active: Optional[bool] = None

class SignalResponse(BaseModel):
    message: str
    signal: SignalOut

class TopSignalsResponse(BaseModel):
    signals: List[SignalOut]
    count: int
    generated_at: datetime

# MT5 Connection Schemas
class MT5ConnectionCreate(BaseModel):
    login: str
    password: str
    server: str
    broker: Optional[str] = None
    account_type: str = "demo"

class MT5ConnectionOut(BaseModel):
    id: int
    broker: Optional[str] = None
    account_type: str
    is_connected: bool
    last_heartbeat: Optional[datetime] = None
    client_version: Optional[str] = None
    total_signals_executed: int
    successful_executions: int
    failed_executions: int
    created_at: datetime

    class Config:
        from_attributes = True

# Signal Execution Schemas
class SignalExecutionCreate(BaseModel):
    signal_id: int
    volume: float = Field(..., gt=0)
    execution_price: Optional[float] = None

class SignalExecutionOut(BaseModel):
    id: int
    signal_id: int
    executed_at: datetime
    execution_price: Optional[float] = None
    volume: float
    order_id: Optional[str] = None
    status: str
    profit_loss: float
    closed_at: Optional[datetime] = None
    close_price: Optional[float] = None
    slippage: Optional[float] = None
    execution_time_ms: Optional[int] = None

    class Config:
        from_attributes = True

# Signal Filter Schemas
class SignalFilter(BaseModel):
    asset: Optional[str] = None
    signal_type: Optional[SignalTypeEnum] = None
    min_reliability: Optional[float] = Field(None, ge=0, le=100)
    max_reliability: Optional[float] = Field(None, ge=0, le=100)
    outcome: Optional[SignalOutcomeEnum] = None
    is_active: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)

# Statistics Schemas
class UserStatsOut(BaseModel):
    total_signals: int
    active_signals: int
    winning_signals: int
    losing_signals: int
    win_rate: float
    total_profit_loss: float
    average_reliability: float
    subscription_status: SubscriptionStatusEnum
    subscription_days_left: Optional[int] = None

# Signal Generation Request
class SignalGenerationRequest(BaseModel):
    asset: str
    force_generate: bool = False
    use_ml: bool = True

    @validator('asset')
    def validate_asset(cls, v):
        return v.upper().strip()

# Error Response Schema
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)