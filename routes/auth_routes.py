from fastapi import APIRouter, Depends

from app.controllers.auth_controller import AuthController
from app.schemas.user_schema import UserLoginRequest, UserRegisterRequest
from app.utils.response import success_response

router = APIRouter(prefix="/auth", tags=["auth"])
controller = AuthController()


@router.post("/register")
async def register(payload: UserRegisterRequest):
    result = await controller.register(payload)
    return result


@router.post("/login")
async def login(payload: UserLoginRequest):
    result = await controller.login(payload)
    return result
