from fastapi import APIRouter, HTTPException
from modules.models import AddUserRequest
from fastapi.responses import JSONResponse
from utils.settings import database

user_router = APIRouter()


@user_router.post("/add_user")
async def add_user(data: AddUserRequest):
    try:
        user_id = data.user_id
        conversation_id = data.conversation_id

        # Add user with an empty list for conversation_ids
        database.add_user(user_id, list())

        # Conversation_id is not None if the user has tried before login
        if conversation_id:
            database.add_conversation(user_id, conversation_id, "First Chat")

        return JSONResponse(status_code=200, content={"message": "User added successfully"})
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})


@user_router.get("/load_conversations")
async def get_user_conversations(user_id: str):
    conversations = database.get_user_conversations(user_id)
    if conversations is not None:
        return JSONResponse(status_code=200,
                            content={"message": "Conversation list loaded successfully",
                                     "conversations": conversations})
    else:
        raise HTTPException(status_code=404,
                            detail=f"User ID {user_id} not found in database")
