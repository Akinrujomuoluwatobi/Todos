from typing import Annotated

from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from fastapi import APIRouter, Depends, HTTPException
from database import sessionLocal
from models import Users
from .auth import get_current_user

router = APIRouter(
    prefix='/user',
    tags=['users']
)


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


class UpdatePhoneNumberRequest(BaseModel):
    phone_number: str = Field(min_length=6)


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bycrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not Authenticated')

    user_id: int = user.get('id')

    user_model = db.query(Users).filter(Users.id == user_id).first()

    return user_model


@router.put('/change_password', status_code=status.HTTP_200_OK)
async def change_password(db: db_dependency, user: user_dependency, change_password_request: ChangePasswordRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not Authenticated')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bycrypt_context.verify(change_password_request.old_password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Error on password change')
    user_model.hashed_password = bycrypt_context.hash(change_password_request.new_password)
    db.add(user_model)
    db.commit()


@router.put('/update_phone_number', status_code=status.HTTP_200_OK)
async def update_phone_number(db: db_dependency, user: user_dependency, phoneNumberRequest: UpdatePhoneNumberRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not authenticated')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User record not found')

    user_model.phone_number = phoneNumberRequest.phone_number
    db.add(user_model)
    db.commit()
