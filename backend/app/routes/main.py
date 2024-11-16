from fastapi import APIRouter

from . import calendars
from . import users

api_router = APIRouter()
api_router.include_router(users.router, tags=["users"])
api_router.include_router(calendars.router, tags=["calendars"])
