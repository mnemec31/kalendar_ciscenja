from sqlmodel import Session, select

from app.models.users import User, UserCreate
from app.security import get_password_hash, verify_password


def get_user_by_username(session: Session, username: str) -> User | None:
    user = session.exec(select(User).where(User.username == username)).first()
    return user


def authenticate_user(session: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(session, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(session: Session, user_create: UserCreate) -> User:
    user_in_db = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(user_in_db)
    session.commit()
    session.refresh(user_in_db)
    return user_in_db
