
from fastapi import APIRouter, HTTPException

router = APIRouter()

# ================================================================================================================================================================
# /run/whois
# ================================================================================================================================================================

@router.get(
    "/run/whois", 
    tags=["Tests In Planning"],
    )
async def run_whois():
    return [{"coming": "soon"}, {"quack": "quack"}]