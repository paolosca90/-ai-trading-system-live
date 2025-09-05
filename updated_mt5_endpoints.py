# Add these endpoints to your main.py or create a separate router

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

# Your existing imports
from database import get_db
from jwt_auth import get_current_active_user
from models import User, MT5Connection
from mt5_bridge_client import mt5_client
from crypto_utils import credentials_crypto

# New MT5 schemas
from schemas import (
    MT5ConnectionCreate, MT5ConnectionOut, MT5AccountInfo, 
    MT5RatesRequest, MT5RatesResponse, MT5StatusResponse
)

router = APIRouter(prefix="/mt5", tags=["MT5 Integration"])

@router.post("/connect", response_model=dict)
async def setup_mt5_connection(
    connection_data: MT5ConnectionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Setup or update MT5 connection for user"""
    try:
        # Test connection with bridge first
        bridge_health = await mt5_client.health_check()
        if not bridge_health.get("status") == "healthy":
            raise HTTPException(
                status_code=503,
                detail="MT5 Bridge service is not available"
            )

        # Initialize bridge if needed
        await mt5_client.initialize()

        # Test login with provided credentials
        try:
            login_result = await mt5_client.login(
                login=connection_data.login,
                password=connection_data.password,
                server=connection_data.server
            )

            if login_result.get("status") != "success":
                raise HTTPException(
                    status_code=401,
                    detail="Invalid MT5 credentials"
                )

        except HTTPException as e:
            if e.status_code == 503:
                raise HTTPException(
                    status_code=503,
                    detail="Cannot connect to MT5 Bridge service"
                )
            raise HTTPException(
                status_code=401,
                detail="MT5 login failed - check credentials"
            )

        # Encrypt credentials
        encrypted_creds = credentials_crypto.encrypt_credentials(
            login=connection_data.login,
            password=connection_data.password,
            server=connection_data.server
        )

        # Check if connection already exists
        existing_connection = db.query(MT5Connection).filter(
            MT5Connection.user_id == current_user.id
        ).first()

        if existing_connection:
            # Update existing connection
            existing_connection.encrypted_credentials = encrypted_creds
            existing_connection.broker = connection_data.broker
            existing_connection.account_type = connection_data.account_type
            existing_connection.updated_at = datetime.utcnow()
            existing_connection.last_connection = datetime.utcnow()
            existing_connection.is_active = True
            db.commit()

            return {
                "message": "MT5 connection updated successfully",
                "status": "success",
                "account_info": login_result.get("account_info", {})
            }
        else:
            # Create new connection
            new_connection = MT5Connection(
                user_id=current_user.id,
                encrypted_credentials=encrypted_creds,
                broker=connection_data.broker,
                account_type=connection_data.account_type,
                is_active=True,
                last_connection=datetime.utcnow()
            )
            db.add(new_connection)
            db.commit()

            return {
                "message": "MT5 connection configured successfully",
                "status": "success",
                "account_info": login_result.get("account_info", {})
            }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error configuring MT5: {str(e)}"
        )

@router.get("/status", response_model=dict)
async def get_mt5_connection_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get MT5 connection status for current user"""
    try:
        # Get user's MT5 connection from database
        connection = db.query(MT5Connection).filter(
            MT5Connection.user_id == current_user.id
        ).first()

        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No MT5 connection configured"
            )

        # Check bridge health
        try:
            bridge_health = await mt5_client.health_check()
            bridge_connected = bridge_health.get("status") == "healthy"
        except:
            bridge_connected = False

        # If bridge is connected, try to get account info
        account_info = None
        if bridge_connected and connection.is_active:
            try:
                # Decrypt credentials and login
                creds = credentials_crypto.decrypt_credentials(connection.encrypted_credentials)

                # Login to get fresh account info
                login_result = await mt5_client.login(
                    login=creds["login"],
                    password=creds["password"],
                    server=creds["server"]
                )

                if login_result.get("status") == "success":
                    account_info = login_result.get("account_info")

                    # Update last connection time
                    connection.last_connection = datetime.utcnow()
                    db.commit()

            except Exception as e:
                print(f"Error getting account info: {str(e)}")
                # Don't raise error, just return without account info
                pass

        return {
            "status": "success",
            "connection_configured": True,
            "bridge_connected": bridge_connected,
            "account_info": account_info,
            "connection_details": {
                "broker": connection.broker,
                "account_type": connection.account_type,
                "last_connection": connection.last_connection,
                "is_active": connection.is_active
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting MT5 status: {str(e)}"
        )

@router.post("/rates", response_model=dict)
async def get_mt5_rates(
    rates_request: MT5RatesRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get MT5 rates for a symbol"""
    try:
        # Check if user has MT5 connection
        connection = db.query(MT5Connection).filter(
            MT5Connection.user_id == current_user.id,
            MT5Connection.is_active == True
        ).first()

        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active MT5 connection found"
            )

        # Get rates from bridge
        rates_result = await mt5_client.get_rates(
            symbol=rates_request.symbol,
            timeframe=rates_request.timeframe,
            count=rates_request.count,
            date_from=rates_request.date_from,
            date_to=rates_request.date_to
        )

        if rates_result.get("status") != "success":
            raise HTTPException(
                status_code=400,
                detail="Failed to get rates from MT5"
            )

        return {
            "status": "success",
            "symbol": rates_request.symbol,
            "timeframe": rates_request.timeframe,
            "rates": rates_result.get("rates", [])
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting MT5 rates: {str(e)}"
        )

@router.get("/positions", response_model=dict)
async def get_mt5_positions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get MT5 positions for current user"""
    try:
        # Check if user has MT5 connection
        connection = db.query(MT5Connection).filter(
            MT5Connection.user_id == current_user.id,
            MT5Connection.is_active == True
        ).first()

        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active MT5 connection found"
            )

        # Decrypt credentials and login
        creds = credentials_crypto.decrypt_credentials(connection.encrypted_credentials)

        await mt5_client.login(
            login=creds["login"],
            password=creds["password"],
            server=creds["server"]
        )

        # Get positions from bridge
        positions_result = await mt5_client.get_positions()

        if positions_result.get("status") != "success":
            raise HTTPException(
                status_code=400,
                detail="Failed to get positions from MT5"
            )

        return {
            "status": "success",
            "positions": positions_result.get("positions", [])
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting MT5 positions: {str(e)}"
        )

@router.get("/symbols", response_model=dict)
async def get_mt5_symbols(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get available MT5 symbols"""
    try:
        # Check if user has MT5 connection
        connection = db.query(MT5Connection).filter(
            MT5Connection.user_id == current_user.id,
            MT5Connection.is_active == True
        ).first()

        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active MT5 connection found"
            )

        # Get symbols from bridge
        symbols_result = await mt5_client.get_symbols()

        if symbols_result.get("status") != "success":
            raise HTTPException(
                status_code=400,
                detail="Failed to get symbols from MT5"
            )

        return {
            "status": "success",
            "symbols": symbols_result.get("symbols", [])
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting MT5 symbols: {str(e)}"
        )

@router.post("/disconnect")
async def disconnect_mt5(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Disconnect MT5 connection"""
    try:
        connection = db.query(MT5Connection).filter(
            MT5Connection.user_id == current_user.id
        ).first()

        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No MT5 connection found"
            )

        # Deactivate connection
        connection.is_active = False
        connection.updated_at = datetime.utcnow()
        db.commit()

        # Try to logout from bridge
        try:
            await mt5_client.logout()
        except:
            pass  # Don't fail if bridge is not available

        return {"message": "MT5 connection disconnected successfully"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error disconnecting MT5: {str(e)}"
        )
