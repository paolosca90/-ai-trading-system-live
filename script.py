import os
import zipfile

# Creo la cartella per il progetto
project_name = "trading_backend"
if not os.path.exists(project_name):
    os.makedirs(project_name)

# File 1: requirements.txt
requirements_content = """fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
passlib[bcrypt]
python-jose[cryptography]
python-dotenv
pydantic[email]
python-multipart"""

with open(f"{project_name}/requirements.txt", "w") as f:
    f.write(requirements_content)

# File 2: database.py
database_content = """import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()"""

with open(f"{project_name}/database.py", "w") as f:
    f.write(database_content)

# File 3: models.py
models_content = """from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())"""

with open(f"{project_name}/models.py", "w") as f:
    f.write(models_content)

# File 4: schemas.py
schemas_content = """from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    message: str
    user: UserOut"""

with open(f"{project_name}/schemas.py", "w") as f:
    f.write(schemas_content)

# File 5: auth.py
auth_content = """from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    \"\"\"Hash della password con bcrypt\"\"\"
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    \"\"\"Verifica password\"\"\"
    return pwd_context.verify(plain_password, hashed_password)"""

with open(f"{project_name}/auth.py", "w") as f:
    f.write(auth_content)

# File 6: main.py
main_content = """from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal, engine
from models import Base, User
from schemas import UserCreate, UserResponse
from auth import hash_password

# Crea le tabelle
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Trading API", version="1.0.0")

# Dependency per database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Trading API - Vai su /docs per la documentazione"}

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    \"\"\"
    Registra nuovo utente
    \"\"\"
    try:
        # Hash della password
        hashed_password = hash_password(user.password)
        
        # Crea nuovo utente
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        
        # Salva nel database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserResponse(
            message="Utente registrato con successo",
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
        )"""

with open(f"{project_name}/main.py", "w") as f:
    f.write(main_content)

print("File creati nella cartella:", project_name)

# Creo lo zip
zip_filename = f"{project_name}.zip"
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(project_name):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, project_name)
            zipf.write(file_path, arcname)

print(f"\n✅ ZIP creato: {zip_filename}")
print("\nContenuto del progetto:")
for root, dirs, files in os.walk(project_name):
    level = root.replace(project_name, '').count(os.sep)
    indent = ' ' * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = ' ' * 2 * (level + 1)
    for file in files:
        print(f"{subindent}{file}")