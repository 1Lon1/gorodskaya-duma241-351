from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from auth import hash_password, verify_password, create_access_token
from models import User
from schemas import UserRegister, UserLogin, Token
from database import Base, engine, get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from auth import SECRET_KEY, ALGORITHM
import models
from models import Deputy, Commission
from schemas import (
    DeputyCreate,
    DeputyResponse,
    CommissionCreate,
    CommissionResponse,
    MeetingCreate,
    MeetingResponse,
    AttendanceCreate,
    AttendanceResponse
)
security = HTTPBearer()

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Городская Дума — API",
    version="0.1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Недействительный токен"
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Недействительный токен"
        )

    user = db.query(User).filter(
        User.username == username
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Пользователь не найден"
        )

    return user

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "Сервер работает"
    }


@app.post("/api/deputies", response_model=DeputyResponse)
def create_deputy(
    deputy: DeputyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_deputy = Deputy(
        full_name=deputy.full_name,
        party=deputy.party,
        district=deputy.district
    )

    db.add(new_deputy)
    db.commit()
    db.refresh(new_deputy)

    return new_deputy


@app.get("/api/deputies", response_model=list[DeputyResponse])
def get_deputies(
    db: Session = Depends(get_db)
):
    return db.query(Deputy).all()


@app.get("/api/deputies/{deputy_id}", response_model=DeputyResponse)
def get_deputy(
    deputy_id: int,
    db: Session = Depends(get_db)
):
    deputy = db.query(Deputy).filter(
        Deputy.id == deputy_id
    ).first()

    if deputy is None:
        raise HTTPException(
            status_code=404,
            detail="Депутат не найден"
        )


    return deputy
@app.delete("/api/deputies/{deputy_id}")
def delete_deputy(
    deputy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deputy = db.query(Deputy).filter(
        Deputy.id == deputy_id
    ).first()

    if deputy is None:
        raise HTTPException(
            status_code=404,
            detail="Депутат не найден"
        )

    db.delete(deputy)
    db.commit()

    return {
        "message": "Депутат удалён"
    }
@app.post("/api/commissions", response_model=CommissionResponse)
def create_commission(
    commission: CommissionCreate,
    db: Session = Depends(get_db)
):
    new_commission = Commission(
        name=commission.name,
        description=commission.description,
        chairman_id=commission.chairman_id
    )

    db.add(new_commission)
    db.commit()
    db.refresh(new_commission)

    return new_commission


@app.get("/api/commissions", response_model=list[CommissionResponse])
def get_commissions(
    db: Session = Depends(get_db)
):
    return db.query(Commission).all()


@app.get("/api/commissions/{commission_id}", response_model=CommissionResponse)
def get_commission(
    commission_id: int,
    db: Session = Depends(get_db)
):
    commission = db.query(Commission).filter(
        Commission.id == commission_id
    ).first()

    if commission is None:
        raise HTTPException(
            status_code=404,
            detail="Комиссия не найдена"
        )

    return commission
@app.post("/api/meetings", response_model=MeetingResponse)
def create_meeting(
    meeting: MeetingCreate,
    db: Session = Depends(get_db)
):
    new_meeting = models.Meeting(
        commission_id=meeting.commission_id,
        title=meeting.title,
        date=meeting.date,
        location=meeting.location
    )

    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    return new_meeting


@app.get("/api/meetings", response_model=list[MeetingResponse])
def get_meetings(
    db: Session = Depends(get_db)
):
    return db.query(models.Meeting).all()


@app.get("/api/meetings/{meeting_id}", response_model=MeetingResponse)
def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db)
):
    meeting = db.query(models.Meeting).filter(
        models.Meeting.id == meeting_id
    ).first()

    if meeting is None:
        raise HTTPException(
            status_code=404,
            detail="Заседание не найдено"
        )

    return meeting
@app.post(
    "/api/meetings/{meeting_id}/attendance",
    response_model=AttendanceResponse
)
def create_attendance(
    meeting_id: int,
    attendance: AttendanceCreate,
    db: Session = Depends(get_db)
):
    # Проверяем, существует ли заседание
    meeting = db.query(models.Meeting).filter(
        models.Meeting.id == meeting_id
    ).first()

    if meeting is None:
        raise HTTPException(
            status_code=404,
            detail="Заседание не найдено"
        )

    # Проверяем, существует ли депутат
    deputy = db.query(models.Deputy).filter(
        models.Deputy.id == attendance.deputy_id
    ).first()

    if deputy is None:
        raise HTTPException(
            status_code=404,
            detail="Депутат не найден"
        )

    # Проверяем бизнес-правило:
    # один депутат не может иметь две записи
    # посещаемости на одном заседании
    existing = db.query(models.Attendance).filter(
        models.Attendance.meeting_id == meeting_id,
        models.Attendance.deputy_id == attendance.deputy_id
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail="Для этого депутата уже есть запись посещаемости"
        )

    new_attendance = models.Attendance(
        meeting_id=meeting_id,
        deputy_id=attendance.deputy_id,
        status=attendance.status
    )

    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)

    return new_attendance


@app.get(
    "/api/meetings/{meeting_id}/attendance",
    response_model=list[AttendanceResponse]
)
def get_attendance(
    meeting_id: int,
    db: Session = Depends(get_db)
):
    meeting = db.query(models.Meeting).filter(
        models.Meeting.id == meeting_id
    ).first()

    if meeting is None:
        raise HTTPException(
            status_code=404,
            detail="Заседание не найдено"
        )

    return db.query(models.Attendance).filter(
        models.Attendance.meeting_id == meeting_id
    ).all()
@app.post("/api/auth/register")
def register(
    user: UserRegister,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user is not None:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким именем уже существует"
        )

    new_user = User(
        username=user.username,
        password_hash=hash_password(user.password),
        role="user"
    )

    db.add(new_user)
    db.commit()

    return {
        "message": "Пользователь успешно зарегистрирован"
    }
@app.post("/api/auth/login", response_model=Token)
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Неверное имя пользователя или пароль"
        )

    if not verify_password(
        user.password,
        existing_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Неверное имя пользователя или пароль"
        )

    access_token = create_access_token(
        existing_user.username
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
