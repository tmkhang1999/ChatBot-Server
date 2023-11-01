import uvicorn
from fastapi import FastAPI
from modules.routers import chat_router
from utils.settings import config_manager

app = FastAPI()
app.include_router(chat_router, tags=["chat"])

if __name__ == "__main__":
    app_info = config_manager.get("app")
    uvicorn.run(app, host=app_info["host"], port=int(app_info["port"]))
