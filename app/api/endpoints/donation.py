from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud.donation import donations_crud
from app.schemas.donation import DonationDB, DonationCreate
from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.models.user import User
from app.models.charity_project import CharityProject


router = APIRouter(
    prefix='/donation',
    tags=['Donations'])


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude={
        'invested_amount',
        'fully_invested',
        'close_date',
        'user_id'
    },
    response_model_exclude_none=True
)
async def donation_create(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    donation = await donations_crud.create(donation, session, user)
    investing = await donations_crud.investition(session, donation, CharityProject)
    return investing


@router.get(
    '/',
    response_model=List[DonationDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
):
    donations = await donations_crud.get_multi(session)
    return donations


@router.get(
    '/my',
    response_model=List[DonationDB],
    response_model_exclude={
        'invested_amount',
        'fully_invested',
        'close_date',
        'user_id'
    }
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    donations = await donations_crud.get_my_donations(session, user)
    return donations
