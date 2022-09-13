from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/quack" )
async def read_items():
    return [{"quack": "quack"}, {"quackers": "bark"}]