from fastapi import APIRouter, Depends

from app.controllers.user_controller import UserController
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/user", tags=["user"])
controller = UserController()


@router.get("/profile")
async def get_profile(user: dict = Depends(get_current_user)):
    return await controller.get_profile(user)
