from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import game_logic
import player_service
from api.deps import get_current_user

router = APIRouter(prefix="/game", tags=["game"])


class CompleteLevelRequest(BaseModel):
    airport_ident: str


@router.post("/start")
def start_game(username: str = Depends(get_current_user)):
    """Load existing game or create a new one for the authenticated user."""
    game = player_service.load_player_game(username)
    if game is None:
        game = game_logic.new_game(username)
    return game


@router.get("/state")
def get_game_state(username: str = Depends(get_current_user)):
    game = player_service.load_player_game(username)
    if game is None:
        raise HTTPException(status_code=404, detail="No game found. POST /game/start first.")
    return game


@router.post("/complete-level")
def complete_level(body: CompleteLevelRequest, username: str = Depends(get_current_user)):
    game = player_service.load_player_game(username)
    if game is None:
        raise HTTPException(status_code=404, detail="No game found. POST /game/start first.")
    result = game_logic.deliver_lecture(game, body.airport_ident)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
