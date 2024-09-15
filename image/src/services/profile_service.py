from bson import ObjectId
from db.mongodb import db
from fastapi import HTTPException
from models.profile_model import ProfileModel, ProfileCreate, ProfileResponse
import logging
from bson.errors import InvalidId

logger = logging.getLogger(__name__)


class ProfileService:
    @staticmethod
    def get_collection():
        if db.db is None:
            logger.error("Database not initialized")
            raise HTTPException(status_code=500, detail="Database not initialized")
        return db.db.profiles

    @staticmethod
    async def get_profile_by_email(email: str):
        try:
            logger.debug(f"Fetching profile by email: {email}")
            collection = ProfileService.get_collection()
            profile = await collection.find_one({"email": email})
            if profile:
                logger.debug(f"Profile found: {profile}")
                return ProfileResponse.model_validate(profile)
            logger.debug("Profile not found")
            return None
        except Exception as e:
            logger.error(f"Error fetching profile by email: {str(e)}")
            raise

        
    @staticmethod
    async def create_profile(profile: ProfileCreate):
        try:
            logger.debug(f"Creating profile: {profile}")
            collection = ProfileService.get_collection()
            profile_dict = profile.model_dump()
            result = await collection.insert_one(profile_dict)
            created_profile = await collection.find_one({"_id": result.inserted_id})
            logger.debug(f"Created profile: {created_profile}")
            return ProfileResponse.model_validate(created_profile)
        except Exception as e:
            logger.error(f"Error creating profile: {str(e)}")
            raise
    
    @staticmethod
    async def update_profile(profile: ProfileCreate):
        try:
            logger.debug(f"Update profile: {profile}")
            collection = ProfileService.get_collection()
            profile_dict = profile.model_dump()
            update_result = await collection.update_one({"_id": ObjectId(profile_dict["id"])}, {"$set": profile_dict})
            if update_result.modified_count == 0:
                logger.error("No profile was updated.")
                raise HTTPException(status_code=404, detail="Profile not found.")
            updated_profile = await collection.find_one({"_id": ObjectId(profile_dict["id"])})
            logger.debug(f"Update profile: {updated_profile}")
            return ProfileResponse.model_validate(updated_profile)
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            raise