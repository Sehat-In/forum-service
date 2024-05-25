import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine
from routers import posts, comments, likes
import models

from starlette.responses import RedirectResponse

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(likes.router)

@app.get("/")
def main_function():
    return RedirectResponse(url="/docs/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3003)
