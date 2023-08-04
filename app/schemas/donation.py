from pydantic import BaseModel, PositiveInt
from typing import Optional
from datetime import datetime


class DonationBase(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str]


class DonationCreate(DonationBase):
    pass


class DonationDB(DonationBase):
    id: int
    create_date: Optional[datetime]
    user_id: int
    invested_amount: Optional[int]
    fully_invested: bool
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
