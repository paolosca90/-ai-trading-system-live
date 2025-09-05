from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    class Config:
        orm_mode = True

class SignalCreate(BaseModel):
    ticker: str
    strike: float
    expiry: datetime
    side: str

class SignalOut(BaseModel):
    id: int
    ticker: str
    strike: float
    expiry: datetime
    side: str
    entry_time: datetime
    user_id: int
    class Config:
        orm_mode = True