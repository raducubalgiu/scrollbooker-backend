from typing import TypeVar, Optional, Dict, Union, Generic
from fastapi import HTTPException
from pydantic import BaseModel
from starlette import status
from sqlalchemy import select, Table, insert, delete, asc, desc
from app.core.dependencies import DBSession
from app.models import Base
from typing import List, Any, Type
from app.core.logger import logger

ModelType = TypeVar("ModelType", bound=Base)
SchemaIn = TypeVar("SchemaIn", bound=BaseModel)
SchemaOut = TypeVar("SchemaOut", bound=BaseModel)

class PaginatedResponse(BaseModel, Generic[SchemaOut]):
    count: int
    results: List[SchemaOut]

async def db_get_all_paginate(
        db: DBSession,
        model: Type[SchemaIn],
        schema: Type[SchemaOut],
        page: int,
        limit: int,
        filters: Optional[Dict[Any, Any]] = None,
        order_by: Optional[Union[str, List[str]]] = None,
        descending: Optional[bool] = False,
        unique: Optional[bool] = None,
        joins: Optional[List] = None
) -> PaginatedResponse[SchemaOut]:
    query_all = select(model)

    if joins:
        query_all = query_all.options(*joins)

    if filters:
        for field, value in filters.items():
            column = getattr(model, field) if isinstance(field, str) else field
            query_all = query_all.where(column == value)  # type: ignore

    if order_by:
        if isinstance(order_by, str):
            order_by = [order_by]
        for column_name in order_by:
            column = getattr(model, column_name, None)
            if column is not None:
                query_all = query_all.order_by(desc(column) if descending else asc(column))
            else:
                raise ValueError(f"Column '{column_name}' does not exist in {model.__name__}")

    total_query = await db.execute(select(query_all.subquery()))
    total = len(total_query.scalars().all())

    result = await db.execute(query_all.offset((page - 1) * limit).limit(limit))
    items = result.scalars().unique().all() if unique else result.scalars().all()

    results = [schema.model_validate(obj) for obj in items]
    return PaginatedResponse(count=total, results=results)

async def db_get_all(
        db: DBSession,
        model: Type[ModelType],
        filters: Optional[Dict[Any, Any]] = None,
        joins: Optional[List] = None,
        unique: Optional[bool] = None,
        limit: Optional[int] = None,
        page: Optional[int] =None,
        order_by: Optional[Union[str, List[str]]] = None,
        descending: Optional[bool] = False
        ) -> List[ModelType]:

        query_all = select(model)

        if joins:
            query_all = query_all.options(*joins)

        if filters:
            for field, value in filters.items():
                column = getattr(model, field) if isinstance(field, str) else field
                query_all = query_all.where(column == value) #type: ignore

        if order_by:
            if isinstance(order_by, str):
                order_by = [order_by]
            for column_name in order_by:
                column = getattr(model, column_name, None)
                if column is not None:
                    query_all = query_all.order_by(desc(column) if descending else asc(column))
                else:
                    raise ValueError(f"Column '{column_name}' does not exist in {model.__name__}")

        if page and limit:
            query_all = query_all.limit(limit)
            query_all = query_all.offset((page - 1) * limit)

        result = await db.execute(query_all)

        if unique:
            return result.scalars().unique().all()
        else:
            return result.scalars().all()

async def db_get_one(
        db: DBSession,
        model: Type[ModelType],
        filters: Optional[Dict[Any, Any]] = None,
        joins: Optional[List] = None,
        raise_not_found: bool = True
) -> ModelType:
    query_one = select(model)

    if joins:
        for join_option in joins:
            query_one = query_one.options(join_option)

    for field, value in filters.items():
        column = getattr(model, field) if isinstance(field, str) else field
        query_one = query_one.where(column == value)  # type: ignore

    result = await db.execute(query_one)
    instance = result.scalars().first()

    if not instance and raise_not_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{model.__name__} not found")

    return instance

async def db_create(db: DBSession, model: Type[ModelType], create_data: SchemaIn, extra_params: Optional[dict] = None) -> ModelType:
    if create_data is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='No data provided')

    obj_data = create_data.model_dump()
    new_obj = model(**obj_data, **(extra_params or {}))
    db.add(new_obj)
    await db.commit()
    await db.refresh(new_obj)

    return new_obj

async def db_delete(db: DBSession, model: Type[ModelType], resource_id: int):
    db_obj = await db.get(model, resource_id)

    if not db_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{model.__name__} not found")
    await db.delete(db_obj)
    await db.commit()

async def db_update(
        db: DBSession,
        model: Type[ModelType],
        update_data: SchemaIn,
        resource_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        load_options: Optional[list] = None
):
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
        model_one: Type[ModelType],
        resource_one_id: int,
        model_two: Type[ModelType],
        resource_two_id: int,
        relation_table: Table
):
    resource_one = await db.get(model_one, resource_one_id)
    resource_two = await db.get(model_two, resource_two_id)

    if not resource_one or not resource_two:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{model_one.__name__} or {model_two.__name__} not found")

    many_to_many_stmt = await db.execute(
        select(relation_table).where(
            (relation_table.c[list(relation_table.c.keys())[0]] == resource_one_id) & (relation_table.c[list(relation_table.c.keys())[1]] == resource_two_id)  # type: ignore
        )
    )
    many_to_many = many_to_many_stmt.scalar_one_or_none()

    if not many_to_many:
        logger.warning(f"{model_one.__name__} id: {resource_one_id} is not associated with {model_one.__name__} id: {resource_two_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="These resources are not associated")
    return many_to_many


async def db_insert_many_to_many(
        db: DBSession,
        model_one: Type[ModelType],
        resource_one_id: int,
        model_two: Type[ModelType],
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
        model_one: Type[ModelType],
        resource_one_id: int,
        model_two: Type[ModelType],
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