from typing import TypeVar, Optional, Dict, Union, Generic
from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, Table, insert, delete, asc, desc, func, and_
from core.dependencies import DBSession
from models import Base
from typing import List, Any, Type
from core.logger import logger

SchemaT = TypeVar("SchemaT", bound=BaseModel)
ModelT = TypeVar("ModelT", bound=Base)

class PaginatedResponse(BaseModel, Generic[SchemaT]):
    count: int
    results: List[SchemaT]

async def db_get_all(
    db: DBSession,
    model: Type[ModelT],
    filters: Optional[Dict[Any, Any]] = None,
    joins: Optional[List] = None,
    unique: Optional[bool] = None,
    order_by: Optional[Union[str, List[str]]] = None,
    descending: Optional[bool] = False,
    schema: Optional[Type[SchemaT]] = None,
    page: Optional[int] = None,
    limit: Optional[int] = None
) -> Union[List[ModelT], PaginatedResponse[SchemaT]]:
    query_all = select(model)

    if joins:
        query_all = query_all.options(*joins)

    if filters:
        for field, value in filters.items():
            column = getattr(model, field) if isinstance(field, str) else field
            query_all = query_all.where(column == value)

    if order_by:
        if isinstance(order_by, str):
            order_by = [order_by]
        for column_name in order_by:
            column = getattr(model, column_name, None)
            if column is not None:
                query_all = query_all.order_by(desc(column) if descending else asc(column))
            else:
                raise ValueError(f"Column '{column_name}' does not exist in {model.__name__}")

    count_query = select(func.count()).select_from(query_all.subquery())

    if page is not None and limit is not None:
        query_all = query_all.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query_all)
    data = result.scalars().unique().all() if unique else result.scalars().all()

    if schema:
        data = [schema.model_validate(obj) for obj in data]

    if page is not None and limit is not None:
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        return PaginatedResponse(count=total, results=data)

    return data

async def db_get_one(
    db: DBSession,
    model: Type[ModelT],
    filters: Optional[Dict[Any, Any]] = None,
    joins: Optional[List] = None,
    raise_not_found: bool = True
) -> Optional[ModelT]:
    query_one = select(model)

    if joins:
        for join_option in joins:
            query_one = query_one.options(join_option)

    for field, value in filters.items():
        column = getattr(model, field) if isinstance(field, str) else field
        query_one = query_one.where(column == value)

    result = await db.execute(query_one)
    instance = result.scalars().first()

    if not instance and raise_not_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{model.__name__} not found")

    return instance

async def db_create(
    db: DBSession,
    model: Type[ModelT],
    create_data: SchemaT,
    extra_params: Optional[dict] = None
) -> Optional[ModelT]:
    if create_data is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='No data provided')

    obj_data = create_data.model_dump()
    new_obj = model(**obj_data, **(extra_params or {}))
    db.add(new_obj)
    await db.commit()
    await db.refresh(new_obj)

    return new_obj

async def db_delete(
    db: DBSession,
    model: Type[ModelT],
    resource_id: int
):
    db_obj = await db.get(model, resource_id)

    if not db_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{model.__name__} not found")
    await db.delete(db_obj)
    await db.commit()

async def db_update(
    db: DBSession,
    model: Type[ModelT],
    update_data: SchemaT,
    resource_id: Optional[int] = None,
    filters: Optional[Dict[str, Any]] = None,
    load_options: Optional[list] = None
) -> ModelT:
    query_put = select(model)

    if resource_id:
        query_put = query_put.filter(model.id == resource_id) # type: ignore
    elif filters:
        query_put = query_put.filter_by(**filters)
    else:
        raise ValueError("Either 'resource_id' or 'filters' must be provided")

    if load_options:
        query_put = query_put.options(*load_options)

    result = await db.execute(query_put)
    resource = result.scalars().first()

    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{model.__name__} not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if hasattr(resource, key):
            setattr(resource, key, value)

    await db.commit()
    await db.refresh(resource)

    return resource

async def db_get_many_to_many(
    db: DBSession,
    model_one: Type[ModelT],
    resource_one_id: int,
    model_two: Type[ModelT],
    resource_two_id: int,
    relation_table: Table
):
    resource_one = await db.get(model_one, resource_one_id)
    resource_two = await db.get(model_two, resource_two_id)

    if not resource_one or not resource_two:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{model_one.__name__} or {model_two.__name__} not found")

    many_to_many_stmt = await db.execute(
        select(relation_table)
        .where(and_(
            relation_table.c[list(relation_table.c.keys())[0]] == resource_one_id),
            relation_table.c[list(relation_table.c.keys())[1]] == resource_two_id
        )
    )
    many_to_many = many_to_many_stmt.mappings().all()

    return many_to_many if many_to_many else []

async def db_insert_many_to_many(
    db: DBSession,
    model_one: Type[ModelT],
    resource_one_id: int,
    model_two: Type[ModelT],
    resource_two_id: int,
    relation_table: Table
):
    resource_one = await db.get(model_one, resource_one_id)
    resource_two = await db.get(model_two, resource_two_id)

    if not resource_one or not resource_two:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{model_one.__name__} or {model_two.__name__} not found")

    is_present_stmt = await db.execute(
        select(relation_table).where(
            (relation_table.c[list(relation_table.c.keys())[0]] == resource_one_id) & (relation_table.c[list(relation_table.c.keys())[1]] == resource_two_id) #type: ignore
        )
    )
    is_present = is_present_stmt.scalar_one_or_none()

    if is_present:
        logger.warning(f"{model_one.__name__} id: {resource_one_id} is already associated with {model_two.__name__} id: {resource_two_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"These resources are already associated")

    await db.execute(insert(relation_table).values(
        {
            list(relation_table.c.keys())[0]: resource_one_id,
            list(relation_table.c.keys())[1]: resource_two_id
         }
    ))
    await db.commit()
    return {"detail": f"{model_two.__name__} id: {resource_two_id} successfully attached to {model_one.__name__} id: {resource_one_id}"}

async def db_remove_many_to_many(
    db: DBSession,
    model_one: Type[ModelT],
    resource_one_id: int,
    model_two: Type[ModelT],
    resource_two_id: int,
    relation_table: Table
):
    resource_one = await db.get(model_one, resource_one_id)
    resource_two = await db.get(model_two, resource_two_id)

    if not resource_one or not resource_two:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{model_one.__name__} or {model_two.__name__} not found")

    is_present_stmt = await db.execute(
        select(relation_table).where(
            (relation_table.c[list(relation_table.c.keys())[0]] == resource_one_id) & (relation_table.c[list(relation_table.c.keys())[1]] == resource_two_id)  # type: ignore
        )
    )
    is_present = is_present_stmt.scalar_one_or_none()

    if not is_present:
        logger.warning(f"{model_one.__name__} id: {resource_one_id} is not associated with {model_one.__name__} id: {resource_two_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="These resources are not associated")

    await db.execute(delete(relation_table).where(
        (relation_table.c[list(relation_table.c.keys())[0]] == resource_one_id) & (relation_table.c[list(relation_table.c.keys())[1]] == resource_two_id)  # type: ignore
    ))
    await db.commit()