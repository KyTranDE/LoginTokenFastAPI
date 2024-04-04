from fastapi import APIRouter
from modules.GetMatchs import get_matchs


router = APIRouter()

@router.get('/{sport}/{date}')
async def router_get_matchs(sport: str, date: str):
    return get_matchs.get_matchs(sport, date)

