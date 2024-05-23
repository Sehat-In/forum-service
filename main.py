import uvicorn
from fastapi import FastAPI

from database import engine
from routers import posts, comments, likes
import models

from starlette.responses import RedirectResponse

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(likes.router)

@app.get("/")
def main_function():
    return RedirectResponse(url="/docs/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3003)
