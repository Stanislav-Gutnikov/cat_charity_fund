from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Union
from datetime import datetime

from app.models.user import User
from app.models.charity_project import CharityProject
from app.models.donation import Donation


class CRUDBase:

    def __init__(self, model):
        self.model = model

    async def get(
            self,
            obj_id: int,
            session: AsyncSession,
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    async def get_multi(
            self,
            session: AsyncSession
    ):
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
            self,
            obj_in,
            session: AsyncSession,
            user: Optional[User] = None
    ):
        obj_in_data = obj_in.dict()
        if user is not None:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
            self,
            db_obj,
            obj_in,
            session: AsyncSession,
    ):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
            self,
            db_obj,
            session: AsyncSession,
    ):
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    async def investition(
            self,
            session: AsyncSession,
            new_obj: Union[CharityProject, Donation],
            model: Union[CharityProject, Donation]
    ):
        objects = await session.execute(
            select(model).where(
                model.fully_invested is not False
            )
        )
        objects = objects.scalars().all()
        obj_money = new_obj.full_amount
        for obj in objects:
            need_money = obj.full_amount - obj.invested_amount
            if obj_money <= need_money:
                obj.invested_amount += obj_money
                new_obj.invested_amount += obj_money
                obj_money = 0
            else:
                obj.invested_amount = need_money
                new_obj.invested_amount += need_money
                obj_money -= need_money
            if new_obj.full_amount == new_obj.invested_amount:
                new_obj.fully_invested = True
                new_obj.close_date = datetime.now()
            if obj.full_amount == obj.invested_amount:
                obj.fully_invested = True
                obj.close_date = datetime.now()
        await session.commit()
        await session.refresh(new_obj)
        return new_obj
