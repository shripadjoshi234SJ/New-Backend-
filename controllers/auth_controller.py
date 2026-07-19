from datetime import datetime
from typing import Dict

from fastapi import HTTPException, status
from bson import ObjectId

from app.core.database import db
from app.core.security import create_access_token, hash_password, verify_password
from app.schemas.auth_schema import TokenResponse
from app.schemas.user_schema import UserLoginRequest, UserRegisterRequest
from app.utils.response import success_response


class AuthController:
    async def register(self, payload: UserRegisterRequest) -> Dict[str, object]:
        existing = await db["users"].find_one({"email": payload.email.lower()})
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

        user_doc = {
            "_id": str(ObjectId()),
            "name": payload.name.strip(),
            "email": payload.email.lower(),
            "password_hash": hash_password(payload.password),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await db["users"].insert_one(user_doc)

        token = create_access_token(user_doc["_id"])
        return success_response(
            "Registration successful",
            {
                "token": token,
                "user": {"_id": user_doc["_id"], "name": user_doc["name"], "email": user_doc["email"]},
            },
        )

    async def login(self, payload: UserLoginRequest) -> Dict[str, object]:
        user = await db["users"].find_one({"email": payload.email.lower()})
        if not user or not verify_password(payload.password, user.get("password_hash", "")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        token = create_access_token(str(user["_id"]))
        return success_response(
            "Login successful",
            {
                "token": token,
                "user": {"_id": str(user["_id"]), "name": user.get("name"), "email": user.get("email")},
            },
        )
