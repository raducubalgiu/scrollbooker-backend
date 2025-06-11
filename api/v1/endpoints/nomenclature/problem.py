from fastapi import APIRouter
from starlette import status
from backend.core.dependencies import DBSession
from backend.schema.nomenclature.problem import ProblemCreate
from backend.service.nomenclature.problem import create_new_problem

router = APIRouter(prefix="/problems", tags=["Problems"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_problem(db: DBSession, problem_create: ProblemCreate):
    return await create_new_problem(db, problem_create)