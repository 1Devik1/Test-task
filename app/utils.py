import os
import json
import jwt
import datetime
import aiofiles

from passlib.context import CryptContext
from fastapi.exceptions import HTTPException
from typing import Dict, Any
from app.models import User

app_dir = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(app_dir, '..', 'data/data.json')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "MEGASECRET"
TOKEN_LIFE = 60  # в минутах


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(username: str) -> str:
    token_data = {
        "sub": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=TOKEN_LIFE)
    }
    return jwt.encode(token_data, SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истек.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Неверный токен.")


async def read_data() -> Dict[str, Any]:
    try:
        async with aiofiles.open(DATA_FILE, 'r', encoding='utf-8') as f:
            contents = await f.read()
            return json.loads(contents)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


async def write_data(data: Dict[str, Any]) -> None:
    async with aiofiles.open(DATA_FILE, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=4))
