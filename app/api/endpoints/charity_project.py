from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from app.crud.charity_project import charity_projects_crud
from app.schemas.charity_project import CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.models.charity_project import CharityProject
from app.models.donation import Donation


'''Сделать одну ф-цию из двух и в /crud/base
   Убрать валидаторы в отдельный файл'''


async def invest_projects(
        session: AsyncSession,
        project: CharityProject
):
    donations = await session.execute(
        select(Donation).where(
            Donation.fully_invested is not False
        ))
    donations = donations.scalars().all()
    project_money = project.full_amount
    for donation in donations:
        need_money = donation.full_amount - donation.invested_amount
        if project_money <= need_money:
            donation.invested_amount += project_money
            project.invested_amount += project_money
            project_money = 0

        else:
            donation.invested_amount = need_money
            project.invested_amount += need_money
            project_money -= need_money
        if project.full_amount == project.invested_amount:
            project.fully_invested = True
            project.close_date = datetime.now()
        if donation.full_amount == donation.invested_amount:
            donation.fully_invested = True
            donation.close_date = datetime.now()
    await session.commit()
    await session.refresh(project)
    return project


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
    if project_id is not None:
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!'
        )

    new_project = await charity_projects_crud.create(project, session)
    investing = await invest_projects(session, new_project)
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
    if db_project is None:
        raise HTTPException(
            status_code=400,
            detail='Проект не найден'
        )
    if db_project.fully_invested is True:
        raise HTTPException(
            status_code=400,
            detail='Закрытый проект нельзя редактировать!'
        )
    if new_project.full_amount is not None and db_project.invested_amount > new_project.full_amount:
        raise HTTPException(
            status_code=400
        )
    project_name = await charity_projects_crud.get_project_id_by_name(new_project.name, session)
    if project_name is not None:
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!'
        )
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
    if db_project is None:
        raise HTTPException(
            status_code=404,
            detail='Проект не найден'
        )
    if db_project.fully_invested is True or db_project.invested_amount != 0:
        raise HTTPException(
            status_code=400,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
    delete_project = await charity_projects_crud.remove(db_project, session)
    return delete_project