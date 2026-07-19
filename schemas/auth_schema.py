from pydantic import BaseModel


class TokenResponse(BaseModel):
    token: str
    user: dict
