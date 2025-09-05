from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from typing import List, Optional

# Import our modules
from database import SessionLocal, engine
from models import Base, User, Signal, Subscription, MT5Connection, SignalExecution
from schemas import (
    UserCreate, UserResponse, UserLogin, Token, SignalCreate, SignalOut,
    SignalResponse, TopSignalsResponse, MT5ConnectionCreate, MT5ConnectionOut,
    SignalExecutionCreate, SignalExecutionOut, SignalFilter, UserStatsOut
)
from jwt_auth import (
    authenticate_user, create_access_token, create_refresh_token,
    get_current_user, get_current_active_user, hash_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="Trading Signals API",
    description="Professional Trading Signals Platform with AI and MT5 Integration",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Trading Signals API v2.0",
        "status": "active",
        "endpoints": "/docs for API documentation"
    }

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# ========== AUTHENTICATION ENDPOINTS ==========

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register new user with automatic trial subscription"""
    try:
        # Hash password
        hashed_password = hash_password(user.password)

        # Create user
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )

        db.add(db_user)
        db.flush()  # Get user ID

        # Create trial subscription
        trial_end = datetime.utcnow() + timedelta(days=7)  # 7-day trial
        subscription = Subscription(
            user_id=db_user.id,
            status="TRIAL",
            plan_name="trial",
            end_date=trial_end
        )

        db.add(subscription)
        db.commit()
        db.refresh(db_user)

        return UserResponse(
            message="Utente registrato con successo. Trial di 7 giorni attivato!",
            user=db_user
        )

    except IntegrityError as e:
        db.rollback()
        error_info = str(e.orig)

        if "username" in error_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username già esistente"
            )
        elif "email" in error_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email già registrata"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore durante la registrazione"
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore interno del server"
        )

@app.post("/token", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user and return JWT tokens"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o password incorretti",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.get("/me", response_model=UserStatsOut)
def get_current_user_info(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get current user information with statistics"""

    # Get user signals statistics
    total_signals = db.query(Signal).filter(Signal.user_id == current_user.id).count()
    active_signals = db.query(Signal).filter(
        Signal.user_id == current_user.id, 
        Signal.is_active == True
    ).count()
    winning_signals = db.query(Signal).filter(
        Signal.user_id == current_user.id,
        Signal.outcome == "WIN"
    ).count()
    losing_signals = db.query(Signal).filter(
        Signal.user_id == current_user.id,
        Signal.outcome == "LOSS"  
    ).count()

    # Calculate win rate
    total_completed = winning_signals + losing_signals
    win_rate = (winning_signals / total_completed * 100) if total_completed > 0 else 0

    # Get total P&L
    total_pnl_result = db.query(Signal).filter(Signal.user_id == current_user.id).all()
    total_profit_loss = sum([s.profit_loss for s in total_pnl_result if s.profit_loss])

    # Get average reliability
    avg_reliability_result = db.query(Signal).filter(Signal.user_id == current_user.id).all()
    avg_reliability = sum([s.reliability for s in avg_reliability_result]) / len(avg_reliability_result) if avg_reliability_result else 0

    # Get subscription info
    subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    subscription_status = subscription.status if subscription else "INACTIVE"
    days_left = None
    if subscription and subscription.end_date:
        days_left = max(0, (subscription.end_date - datetime.utcnow()).days)

    return UserStatsOut(
        total_signals=total_signals,
        active_signals=active_signals,
        winning_signals=winning_signals,
        losing_signals=losing_signals,
        win_rate=round(win_rate, 2),
        total_profit_loss=round(total_profit_loss, 2),
        average_reliability=round(avg_reliability, 2),
        subscription_status=subscription_status,
        subscription_days_left=days_left
    )

# ========== SIGNAL ENDPOINTS ==========

@app.get("/signals/top", response_model=TopSignalsResponse)
def get_top_signals(db: Session = Depends(get_db)):
    """Get top 3 public signals with highest reliability"""

    top_signals = db.query(Signal).filter(
        Signal.is_public == True,
        Signal.is_active == True,
        Signal.reliability >= 70.0
    ).order_by(Signal.reliability.desc()).limit(3).all()

    return TopSignalsResponse(
        signals=top_signals,
        count=len(top_signals),
        generated_at=datetime.utcnow()
    )

@app.get("/signals", response_model=List[SignalOut])
def get_user_signals(
    filter_params: SignalFilter = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user signals with filtering"""

    query = db.query(Signal).filter(Signal.user_id == current_user.id)

    # Apply filters
    if filter_params.asset:
        query = query.filter(Signal.asset.ilike(f"%{filter_params.asset}%"))
    if filter_params.signal_type:
        query = query.filter(Signal.signal_type == filter_params.signal_type)
    if filter_params.min_reliability is not None:
        query = query.filter(Signal.reliability >= filter_params.min_reliability)
    if filter_params.max_reliability is not None:
        query = query.filter(Signal.reliability <= filter_params.max_reliability)
    if filter_params.outcome:
        query = query.filter(Signal.outcome == filter_params.outcome)
    if filter_params.is_active is not None:
        query = query.filter(Signal.is_active == filter_params.is_active)
    if filter_params.date_from:
        query = query.filter(Signal.created_at >= filter_params.date_from)
    if filter_params.date_to:
        query = query.filter(Signal.created_at <= filter_params.date_to)

    # Apply pagination
    signals = query.offset(filter_params.offset).limit(filter_params.limit).all()

    return signals

@app.post("/signals", response_model=SignalResponse, status_code=status.HTTP_201_CREATED)
def create_signal(
    signal_data: SignalCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new trading signal (admin only for now)"""

    # For now, only admin can create signals manually
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli admin possono creare segnali manualmente"
        )

    try:
        # Create signal with basic data
        new_signal = Signal(
            user_id=current_user.id if not signal_data.is_public else None,
            asset=signal_data.asset,
            signal_type=signal_data.signal_type,
            entry_price=signal_data.entry_price,
            stop_loss=signal_data.stop_loss,
            take_profit=signal_data.take_profit,
            reliability=75.0,  # Default reliability
            is_public=signal_data.is_public,
            current_price=signal_data.entry_price,
            gemini_explanation="Segnale creato manualmente dall'admin",
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )

        db.add(new_signal)
        db.commit()
        db.refresh(new_signal)

        return SignalResponse(
            message="Segnale creato con successo",
            signal=new_signal
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore nella creazione del segnale: {str(e)}"
        )

# ========== MT5 CONNECTION ENDPOINTS ==========

@app.post("/mt5/connect", response_model=dict)
def setup_mt5_connection(
    connection_data: MT5ConnectionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Setup or update MT5 connection for user"""

    try:
        # Check if connection already exists
        existing_connection = db.query(MT5Connection).filter(
            MT5Connection.user_id == current_user.id
        ).first()

        # TODO: Encrypt credentials before storing
        # For now, we'll store a placeholder
        encrypted_creds = f"encrypted_data_for_user_{current_user.id}"

        if existing_connection:
            # Update existing connection
            existing_connection.encrypted_credentials = encrypted_creds
            existing_connection.broker = connection_data.broker
            existing_connection.account_type = connection_data.account_type
            existing_connection.updated_at = datetime.utcnow()
            db.commit()

            return {"message": "Connessione MT5 aggiornata con successo"}
        else:
            # Create new connection
            new_connection = MT5Connection(
                user_id=current_user.id,
                encrypted_credentials=encrypted_creds,
                broker=connection_data.broker,
                account_type=connection_data.account_type
            )

            db.add(new_connection)
            db.commit()

            return {"message": "Connessione MT5 configurata con successo"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore nella configurazione MT5: {str(e)}"
        )

@app.get("/mt5/status", response_model=MT5ConnectionOut)
def get_mt5_connection_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get MT5 connection status for current user"""

    connection = db.query(MT5Connection).filter(
        MT5Connection.user_id == current_user.id
    ).first()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nessuna connessione MT5 configurata"
        )

    return connection

# ========== ADMIN ENDPOINTS ==========

@app.post("/admin/generate-signals")
def generate_signals_manually(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate signals manually (admin only)"""

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # TODO: Implement signal generation
    return {"message": "Signal generation started", "status": "in_progress"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)