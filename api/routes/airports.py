from fastapi import APIRouter, HTTPException, Query
import airport_service

router = APIRouter(prefix="/airports", tags=["airports"])


@router.get("")
def list_airports(
    south: float | None = Query(default=None, ge=-90, le=90),
    north: float | None = Query(default=None, ge=-90, le=90),
    west: float | None = Query(default=None, ge=-180, le=180),
    east: float | None = Query(default=None, ge=-180, le=180),
):
    has_bounds = [south, north, west, east]
    if any(value is not None for value in has_bounds):
        if any(value is None for value in has_bounds):
            raise HTTPException(status_code=400, detail="south, north, west, and east are required together")
        if south > north:
            raise HTTPException(status_code=400, detail="south must be less than or equal to north")

        return airport_service.get_level_airports_in_bounds(south, north, west, east)

    return airport_service.get_level_airports()


@router.get("/{ident}")
def get_airport(ident: str):
    airport = airport_service.get_airport(ident)
    if airport is None:
        raise HTTPException(status_code=404, detail=f"Airport {ident} not found")
    return airport
