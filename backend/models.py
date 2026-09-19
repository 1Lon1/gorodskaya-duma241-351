from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")


class Deputy(Base):
    __tablename__ = "deputies"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(150), nullable=False)
    party = Column(String(100))
    district = Column(String(100))


class Commission(Base):
    __tablename__ = "commissions"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    chairman_id = Column(
        Integer,
        ForeignKey("deputies.id")
    )

    chairman = relationship("Deputy")


class DeputyCommission(Base):
    __tablename__ = "deputy_commissions"

    deputy_id = Column(
        Integer,
        ForeignKey("deputies.id"),
        primary_key=True
    )

    commission_id = Column(
        Integer,
        ForeignKey("commissions.id"),
        primary_key=True
    )


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True)

    commission_id = Column(
        Integer,
        ForeignKey("commissions.id"),
        nullable=False
    )

    title = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)
    location = Column(String(200))

    commission = relationship("Commission")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)

    meeting_id = Column(
        Integer,
        ForeignKey("meetings.id"),
        nullable=False
    )

    deputy_id = Column(
        Integer,
        ForeignKey("deputies.id"),
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False
    )

    meeting = relationship("Meeting")
    deputy = relationship("Deputy")

    __table_args__ = (
        UniqueConstraint(
            "meeting_id",
            "deputy_id",
            name="unique_meeting_deputy"
        ),
    )