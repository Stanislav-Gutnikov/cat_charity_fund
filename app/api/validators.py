from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from http import HTTPStatus

from app.models.charity_project import CharityProject


async def same_name_project_validator(
        session: AsyncSession,
        project_id: int = None
):
    if project_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!'
        )


async def project_exists_validator(
        session: AsyncSession,
        project: CharityProject = None
):
    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект не найден'
        )


async def close_project_validator(
        session: AsyncSession,
        project: CharityProject = None
):
    if project.fully_invested is True:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!'
        )


async def invested_amount_smaller_full_amount_validator(
        new_project: CharityProject,
        db_project: CharityProject,
        session: AsyncSession
):
    if new_project.full_amount is not None and db_project.invested_amount > new_project.full_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST
        )


async def project_invested_validator(
        project: CharityProject,
        session: AsyncSession
):
    if project.fully_invested is True or project.invested_amount != 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
