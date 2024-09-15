from fastapi import APIRouter, HTTPException
from models.profile_model import ProfileCreate, ProfileResponse, ProfileUpdate
from services.profile_service import ProfileService
from pymongo.errors import PyMongoError
from bson.errors import InvalidId

router = APIRouter()


@router.get("/{email}", response_model=ProfileResponse)
async def get_profile_by_email(email: str):
    try:
        profile = await ProfileService.get_profile_by_email(email)
        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid profile ID format")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/create-profile", response_model=ProfileResponse)
async def create_profile(profile: ProfileCreate):
    try:
        return await ProfileService.create_profile(profile)
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/update-profile", response_model=ProfileResponse)
async def update_building(profile: ProfileUpdate):
    try:
        return await ProfileService.update_profile(profile)
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
