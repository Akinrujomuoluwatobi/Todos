from typing import Annotated

from sqlalchemy.orm import Session

import models
from fastapi import FastAPI, Depends, HTTPException
from database import engine, sessionLocal
from models import Todos

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@app.get("/todo/{todo_id}")
async def read_todo(db: db_dependency, todo_id: int):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model

    raise HTTPException(404, "Todos not found")
