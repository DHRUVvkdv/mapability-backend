from fastapi import APIRouter, HTTPException
from models.user_model import UserCreate, UserResponse
from services.user_service import UserService
from pymongo.errors import PyMongoError
from bson.errors import InvalidId

router = APIRouter()

@router.get("/get-users", response_model=list[UserResponse])
async def read_users():
    try:
        return await UserService.get_users()
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/create-user", response_model=UserResponse)
async def create_user(user: UserCreate):
    try:
        return await UserService.create_user(user)
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")




@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: str):
    try:
        user = await UserService.get_user(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserCreate):
    try:
        updated_user = await UserService.update_user(user_id, user)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.delete("/{user_id}", response_model=bool)
async def delete_user(user_id: str):
    try:
        deleted = await UserService.delete_user(user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="User not found")
        return True
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
