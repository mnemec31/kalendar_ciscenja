from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.deps import SessionDep
from app.config import settings
from app.models.users import Token, UserCreate, UserPublic
from app.security import create_access_token
from app import crud

router = APIRouter()


@router.post("/token")
async def login_for_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = crud.authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register", response_model=UserPublic)
async def register(session: SessionDep, user_create: UserCreate):
    if len(user_create.username) < 3 or len(user_create.password) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password must be at least 3 characters long",
        )

    user_in_db = crud.get_user_by_username(session, user_create.username)
    if user_in_db is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    user_in_db = crud.create_user(session=session, user_create=user_create)

    return user_in_db
