from fastapi import APIRouter
import db_manager

router = APIRouter(prefix="/scores", tags=["scores"])


@router.get("")
def get_scores():
    """Public endpoint — no auth required. Returns top 20 players by money."""
    return db_manager.get_top_scores(limit=20)
