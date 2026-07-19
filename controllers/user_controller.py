from typing import Dict

from fastapi import HTTPException, status

from app.core.database import db
from app.utils.response import success_response


class UserController:
    async def get_profile(self, user: dict) -> Dict[str, object]:
        user_doc = await db["users"].find_one({"_id": user["id"]})
        if not user_doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return success_response(
            "Profile fetched",
            {"_id": str(user_doc["_id"]), "name": user_doc.get("name"), "email": user_doc.get("email")},
        )
