from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import ping_database
from app.middleware.cors import add_cors_middleware
from app.middleware.error_handler import register_error_handlers
from app.routes.auth_routes import router as auth_router
from app.routes.note_routes import router as note_router
from app.routes.user_routes import router as user_router

app = FastAPI(title="AI Smart Notes Summarizer API", version="1.0.0")

add_cors_middleware(app)
register_error_handlers(app)

app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(note_router, prefix="/api")


@app.get("/health")
async def health_check():
    is_ready = await ping_database()
    return JSONResponse(content={"status": "ok", "database": "connected" if is_ready else "unavailable"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=False)
