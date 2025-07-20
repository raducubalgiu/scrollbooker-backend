from fastapi import APIRouter
from fastapi.params import Query

from core.dependencies import DBSession
from schema.search.search import SearchResponse
from service.search.search import search_keyword

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/",
            summary='Search keywords, users, services or business types',
            response_model=list[SearchResponse])
async def search(db: DBSession, query: str = Query(min_length=1)):
    return await search_keyword(db, query)