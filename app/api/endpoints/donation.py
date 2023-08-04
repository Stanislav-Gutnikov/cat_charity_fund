from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
from sqlalchemy import select

from app.crud.donation import donations_crud
from app.schemas.donation import DonationDB, DonationCreate
from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.models.user import User
from app.models.charity_project import CharityProject
from app.models.donation import Donation


async def invest_donation(
        session: AsyncSession,
        donation: Donation
):
    projects = await session.execute(
        select(CharityProject).where(
            CharityProject.full_amount > CharityProject.invested_amount
        ))
    projects = projects.scalars().all()
    donation_money = donation.full_amount
    for project in projects:
        need_money = project.full_amount - project.invested_amount
        if donation_money <= need_money:
            project.invested_amount += donation_money
            donation.invested_amount += donation_money
            donation_money = 0

        else:
            project.invested_amount = need_money
            donation.invested_amount += need_money
            donation_money -= need_money
        if donation.full_amount == donation.invested_amount:
            donation.fully_invested = True
            donation.close_date = datetime.now()
        if project.full_amount == project.invested_amount:
            project.fully_invested = True
            project.close_date = datetime.now()
    await session.commit()
    await session.refresh(donation)
    return donation


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
    investing = await invest_donation(session, donation)
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
