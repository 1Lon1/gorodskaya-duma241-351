from datetime import date
from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class DeputyCreate(BaseModel):
    full_name: str
    party: str | None = None
    district: str | None = None


class DeputyResponse(BaseModel):
    id: int
    full_name: str
    party: str | None
    district: str | None

    class Config:
        from_attributes = True


class CommissionCreate(BaseModel):
    name: str
    description: str | None = None
    chairman_id: int | None = None


class CommissionResponse(BaseModel):
    id: int
    name: str
    description: str | None
    chairman_id: int | None

    class Config:
        from_attributes = True


class MeetingCreate(BaseModel):
    commission_id: int
    title: str
    date: date
    location: str | None = None


class MeetingResponse(BaseModel):
    id: int
    commission_id: int
    title: str
    date: date
    location: str | None

    class Config:
        from_attributes = True


class AttendanceCreate(BaseModel):
    deputy_id: int
    status: str


class AttendanceResponse(BaseModel):
    id: int
    meeting_id: int
    deputy_id: int
    status: str

    class Config:
        from_attributes = True