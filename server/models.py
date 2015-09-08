import datetime

from sqlalchemy import Column, Boolean, Integer, BigInteger, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

SESSION_SHELF_LIFE = datetime.timedelta(days=1)

Base = declarative_base()

class Session(Base):
    __tablename__ = 'session'
    id = Column(Integer, primary_key=True, autoincrement=True)
    issued_at = Column(DateTime, default=datetime.datetime.now)
    user_id = Column(Integer, ForeignKey('user.id'))

    @property
    def valid(self):
        return self.issued_at + SESSION_SHELF_LIFE > datetime.datetime.now()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    email = Column(String)
    rating = Column(Integer, default=1400)
    volatility = Column(Integer, default=0)
    sessions = relationship('Session', backref='user')
