from fastapi import FastAPI
from config import engine
import model
import router


model.Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.get('/')
async def home():
    return {"message":"Hello world"}



app.include_router(router.router)