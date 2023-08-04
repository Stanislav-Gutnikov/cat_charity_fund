from sqlalchemy import select
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.donation import Donation
from app.models.user import User
from app.crud.base import CRUDBase


class CRUDDonation(CRUDBase):

    async def get_my_donations(
            self,
            session: AsyncSession,
            user: User
    ) -> List[Donation]:
        donations = await session.execute(select(Donation).where(
            Donation.user_id == user.id
        ))
        return donations.scalars().all()


donations_crud = CRUDDonation(Donation)
