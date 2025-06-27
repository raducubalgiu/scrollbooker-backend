from core.crud_helpers import db_create
from core.dependencies import DBSession
from models.nomenclature.problem import Problem
from schema.nomenclature.problem import ProblemCreate

async def create_new_problem(db: DBSession, problem_create: ProblemCreate):
    return await db_create(db, model=Problem, create_data=problem_create)