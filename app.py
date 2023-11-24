import uvicorn
from fastapi import FastAPI, HTTPException
from modules.routers import trial_router, user_router, chat_router
from utils.settings import config_manager
from starlette.responses import JSONResponse

app = FastAPI()
app.include_router(trial_router, tags=["trial"])
app.include_router(user_router, tags=["user"])
app.include_router(chat_router, tags=["chat"])


@app.get("/healthcheck")
async def healthcheck():
    try:
        # If all checks pass, return a healthy response
        return JSONResponse(status_code=200,
                            content={"status": "OK"})

    except Exception as e:
        # If any checks fail, return an unhealthy response with details
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    app_info = config_manager.get("app")
    uvicorn.run(app, host=app_info["host"], port=int(app_info["port"]))
