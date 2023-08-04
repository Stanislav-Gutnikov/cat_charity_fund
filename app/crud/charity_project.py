from sqlalchemy import select
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import CharityProject
from app.crud.base import CRUDBase


class CRUDCharityProjects(CRUDBase):

    async def get_project_by_id(
            self,
            project_id: int,
            session: AsyncSession
    ) -> CharityProject:
        project = await session.execute(select(CharityProject).where(
            CharityProject.id == project_id
        ))
        return project.scalars().first()

    async def get_project_id_by_name(
            self,
            name: str,
            session: AsyncSession
    ) -> Optional[int]:
        db_project_id = await session.execute(select(
            CharityProject.id
        ).where(
            CharityProject.name == name
        ))
        db_project_id = db_project_id.scalars().first()
        return db_project_id


charity_projects_crud = CRUDCharityProjects(CharityProject)
