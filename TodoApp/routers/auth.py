from fastapi import APIRouter

authRouter = APIRouter()


@authRouter.get("/auth")
async def getUsers():
    return {"User": "user route"}
