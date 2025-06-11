from backend.core.crud_helpers import db_create
from backend.core.dependencies import DBSession
from backend.models.nomenclature.problem import Problem
from backend.schema.nomenclature.problem import ProblemCreate

async def create_new_problem(db: DBSession, problem_create: ProblemCreate):
    return await db_create(db, model=Problem, create_data=problem_create)