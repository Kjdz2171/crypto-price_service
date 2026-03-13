from sqlalchemy import BigInteger, Column, Float, Integer, String

from .database import Base


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticker = Column(String(32), index=True, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(BigInteger, index=True, nullable=False)  # UNIX timestamp (ms)

