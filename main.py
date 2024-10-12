import uvicorn
from fastapi import FastAPI
from src.routes import admin_moderation
from src.routes import auth, photos
from src.middleware.security_middleware import TokenBlacklistMiddleware
from src.routes import rating, search, filter

app = FastAPI()

app.include_router(auth.router)
app.include_router(photos.router)
app.include_router(admin_moderation.router)

app.add_middleware(TokenBlacklistMiddleware)


@app.get("/")
def read_root():
    return {"message": "PhotoShare"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

