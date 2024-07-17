
import models
from fastapi import FastAPI
from database import engine
from routers import auth, todos

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.authRouter)
app.include_router(todos.router)