from sqlalchemy import Column, ForeignKey, Text, Integer
from app.models.charity_project import UniversalClass


class Donation(UniversalClass):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)
