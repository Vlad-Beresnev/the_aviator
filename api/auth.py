from datetime import datetime, timedelta, timezone
import mysql.connector
import bcrypt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from jose import jwt
import db_manager
from api.deps import JWT_SECRET, ALGORITHM

router = APIRouter(prefix="/auth", tags=["auth"])


class AuthRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _create_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    return jwt.encode({"sub": username, "exp": expire}, JWT_SECRET, algorithm=ALGORITHM)


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: AuthRequest):
    conn = db_manager._get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (body.username, hashed.decode())
        )
        conn.commit()
    except mysql.connector.IntegrityError:
        raise HTTPException(status_code=409, detail="Username already taken")
    finally:
        cursor.close()
        conn.close()
    return TokenResponse(access_token=_create_token(body.username))


@router.post("/login", response_model=TokenResponse)
def login(body: AuthRequest):
    conn = db_manager._get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT password_hash FROM users WHERE username = %s", (body.username,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row or not bcrypt.checkpw(body.password.encode(), row["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=_create_token(body.username))
