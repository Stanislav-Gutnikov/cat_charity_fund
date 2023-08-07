from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud.charity_project import charity_projects_crud
from app.schemas.charity_project import CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.models.donation import Donation
from app.api.validators import (
    same_name_project_validator,
    project_exists_validator,
    close_project_validator,
    invested_amount_smaller_full_amount_validator,
    project_invested_validator
)


router = APIRouter(
    prefix='/charity_project',
    tags=['Charity Projects'])


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def create_new_charity_project(
    project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session)
):
    project_id = await charity_projects_crud.get_project_id_by_name(project.name, session)
    await same_name_project_validator(session=session, project_id=project_id)
    new_project = await charity_projects_crud.create(project, session)
    investing = await charity_projects_crud.investition(session, new_project, Donation)
    return investing


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True
)
async def get_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    projects = await charity_projects_crud.get_multi(session)
    return projects


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def update_charity_project(
    project_id: int,
    new_project: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    db_project = await charity_projects_crud.get_project_by_id(project_id, session)
    await project_exists_validator(session=session, project=db_project)
    await close_project_validator(session=session, project=db_project)
    await invested_amount_smaller_full_amount_validator(session=session, new_project=new_project, db_project=db_project)
    db_project_id = await charity_projects_crud.get_project_id_by_name(new_project.name, session)
    await same_name_project_validator(session=session, project_id=db_project_id)
    update_project = await charity_projects_crud.update(db_project, new_project, session)
    return update_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_project = await charity_projects_crud.get_project_by_id(project_id, session)
    await project_exists_validator(session=session, project=db_project)
    await project_invested_validator(session=session, project=db_project)
    delete_project = await charity_projects_crud.remove(db_project, session)
    return delete_project