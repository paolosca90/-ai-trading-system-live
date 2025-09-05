from fastapi import FastAPI, Depends, HTTPException, status
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
    """
    Registra nuovo utente
    """
    try:
        # DEBUG: stampo i dati ricevuti
        print("REGISTRO:", user)

        # Hash della password
        hashed_password = hash_password(user.password)
        print("HASH PASSWORD OK")

        # Crea nuovo utente
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )

        # Salva nel database
        db.add(db_user)
        print("USER AGGIUNTO AL DB")
        db.commit()
        print("COMMIT OK")
        db.refresh(db_user)
        print("USER SALVATO OK")

        return UserResponse(
            message="Utente registrato con successo",
            user=db_user
        )

    except IntegrityError as e:
        db.rollback()
        error_info = str(e.orig)
        print("ERRORE INTEGRITY:", error_info)

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
        print("ERRORE REGISTER:", repr(e))
        print("TIPO ERRORE:", type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore interno del server"
        )