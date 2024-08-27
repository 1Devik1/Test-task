import pyaspeller

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from typing import List, Dict

from app.models import User, Note
from app.utils import read_data, write_data, hash_password, verify_password, create_token, verify_token

router = APIRouter()
speller = pyaspeller.YandexSpeller()
auth_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register")
async def register(user: User) -> Dict[str, str]:
    data = await read_data()
    if user.username in data:
        raise HTTPException(status_code=400, detail="Такой пользователь уже есть!")

    hashed_password = hash_password(user.password)
    data[user.username] = {"password": hashed_password, "notes": []}
    await write_data(data)

    return {"message": "Пользователь зарегестрирован!"}


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    data = await read_data()
    if data is None or not verify_password(form_data.password, data[form_data.username]['password']):
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль.")

    access_token = create_token(form_data.username)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/notes")
async def create_note(note: Note, token: str = Depends(auth_scheme)) -> Dict[str, str]:
    username = verify_token(token)
    data = await read_data()

    note.title = speller.spelled(note.title)
    note.content = speller.spelled(note.content)

    data[username]["notes"].append(note.dict())
    await write_data(data)

    return {"message": "Заметка добавлена", "title": note.title, "content": note.content}


@router.get("/notes")
async def get_note(token: str = Depends(auth_scheme)) -> List[Dict[str, str]]:
    username = verify_token(token)
    data = await read_data()
    notes = data[username]["notes"]

    return notes if len(notes) else [{"message": "Ваши заметки пусты :("}]
