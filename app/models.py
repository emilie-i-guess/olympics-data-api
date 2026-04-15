from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class OlympicResult(Base):
    __tablename__ = "olympic-results"

    # Internal primary key
    id = Column(Integer, primary_key=True, index=True)

    athlete_id = Column(Integer, index=True)
    name = Column(String)
    sex = Column(String(1))
    age = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    team = Column(String)
    noc = Column(String(3), index=True)
    games = Column(String)
    year = Column(Integer, index=True)
    season = Column(String)
    city = Column(String)
    sport = Column(String, index=True)
    event = Column(String)
    medal = Column(String, nullable=True)


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Starter tokens
    tokens = Column(Integer, default=100)
