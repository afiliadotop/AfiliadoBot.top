import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt # PyJWT

logger = logging.getLogger(__name__)

# Secret key for JWT (in production, use env var)
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day

class AuthService:
    def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        # Mock Login Logic
        # In production, verify against Supabase Auth or DB table
        if email == "admin@afiliado.top" and password == "admin":
            return self._create_token({"sub": email, "role": "admin", "name": "Administrador"})
        
        return None

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

    def _create_token(self, data: dict) -> Dict[str, Any]:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return {
            "access_token": encoded_jwt,
            "token_type": "bearer",
            "user": {
                "email": data["sub"],
                "name": data["name"],
                "role": data["role"]
            }
        }

auth_service = AuthService()
