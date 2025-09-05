from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum

# Enums for database
class SignalType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class SignalOutcome(enum.Enum):
    WIN = "WIN"
    LOSS = "LOSS"
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"

class SubscriptionStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"
    TRIAL = "TRIAL"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    signals = relationship("Signal", back_populates="user")
    mt5_connection = relationship("MT5Connection", back_populates="user", uselist=False)
    signal_executions = relationship("SignalExecution", back_populates="user")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)
    plan_name = Column(String, default="basic")
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True))
    auto_renew = Column(Boolean, default=True)
    payment_method = Column(String)  # stripe_id, paypal_id, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="subscription")

class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # NULL for public signals
    asset = Column(String, nullable=False, index=True)  # EURUSD, BTCUSD, etc.
    signal_type = Column(Enum(SignalType), nullable=False)
    reliability = Column(Float, nullable=False)  # 0-100%

    # Price levels
    entry_price = Column(Float)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    current_price = Column(Float)

    # Analysis data
    gemini_explanation = Column(Text)
    ml_confidence = Column(Float)  # 0-1
    market_conditions = Column(JSON)  # Store analysis data

    # Technical indicators
    price_action_score = Column(Float)
    volume_score = Column(Float)
    momentum_score = Column(Float)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    is_public = Column(Boolean, default=False)  # For top signals
    is_active = Column(Boolean, default=True)

    # Outcome tracking
    outcome = Column(Enum(SignalOutcome), default=SignalOutcome.PENDING)
    profit_loss = Column(Float, default=0.0)
    execution_time_ms = Column(Integer)

    # Relationships
    user = relationship("User", back_populates="signals")
    executions = relationship("SignalExecution", back_populates="signal")

class MT5Connection(Base):
    __tablename__ = "mt5_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Connection settings (encrypted)
    encrypted_credentials = Column(Text)  # JSON with login, password, server
    broker = Column(String)
    account_type = Column(String)  # demo, real

    # Connection status
    is_connected = Column(Boolean, default=False)
    last_heartbeat = Column(DateTime(timezone=True))
    client_version = Column(String)
    ip_address = Column(String)

    # Performance tracking
    total_signals_executed = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="mt5_connection")

class SignalExecution(Base):
    __tablename__ = "signal_executions"

    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Execution details
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    execution_price = Column(Float)
    volume = Column(Float)  # Lot size
    order_id = Column(String)  # MT5 order ID

    # Result tracking
    status = Column(String)  # filled, partial, rejected, cancelled
    profit_loss = Column(Float, default=0.0)
    closed_at = Column(DateTime(timezone=True))
    close_price = Column(Float)

    # Execution metrics
    slippage = Column(Float)  # Difference between expected and actual price
    execution_time_ms = Column(Integer)

    # Relationships
    signal = relationship("Signal", back_populates="executions")
    user = relationship("User", back_populates="signal_executions")

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # OHLCV data
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Float)

    # Additional data
    spread = Column(Float)
    tick_volume = Column(Integer)

    # Technical analysis cache
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    rsi_14 = Column(Float)
    macd = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, nullable=False)  # INFO, WARNING, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    module = Column(String)  # signal_engine, ml_model, mt5_bridge, etc.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Additional context
    context_data = Column(JSON)
    stack_trace = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)