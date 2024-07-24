from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from fastapi import APIRouter, Depends, HTTPException, Path
from database import sessionLocal
from models import Todos
from .auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/', status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency, user: user_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(401, detail='Authentication Failed')

    return db.query(Todos).all()


@router.delete('/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, user: user_dependency, todo_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(404, detail='Todo not found')

    db.delete(todo_model)
    db.commit()
