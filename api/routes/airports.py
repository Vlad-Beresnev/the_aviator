from fastapi import APIRouter, Depends, HTTPException
import airport_service
from api.deps import get_current_user

router = APIRouter(prefix="/airports", tags=["airports"])


@router.get("")
def list_airports(_: str = Depends(get_current_user)):
    return airport_service.get_level_airports()


@router.get("/{ident}")
def get_airport(ident: str, _: str = Depends(get_current_user)):
    airport = airport_service.get_airport(ident)
    if airport is None:
        raise HTTPException(status_code=404, detail=f"Airport {ident} not found")
    return airport
