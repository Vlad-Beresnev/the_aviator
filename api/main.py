from contextlib import asynccontextmanager
from fastapi import FastAPI
import db_manager
from api.auth import router as auth_router
from api.routes.airports import router as airports_router
from api.routes.game import router as game_router
from api.routes.scores import router as scores_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_manager.run_migrations()
    yield


app = FastAPI(title="The Aviator API", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(airports_router)
app.include_router(game_router)
app.include_router(scores_router)


@app.get("/health")
def health():
    return {"status": "ok"}
