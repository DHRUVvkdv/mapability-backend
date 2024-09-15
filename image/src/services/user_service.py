from bson import ObjectId
from db.mongodb import db
from fastapi import HTTPException
from models.user_model import UserModel, UserCreate, UserResponse
import logging
from bson.errors import InvalidId

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    def get_collection():
        if db.db is None:
            logger.error("Database not initialized")
            raise HTTPException(status_code=500, detail="Database not initialized")
        return db.db.users

    @staticmethod
    async def get_users():
        try:
            logger.debug("Fetching all users")
            collection = UserService.get_collection()
            users = await collection.find().to_list(1000)
            logger.debug(f"Fetched users: {users}")
            return [UserResponse.model_validate(user) for user in users]
        except Exception as e:
            logger.error(f"Error fetching users: {str(e)}")
            raise
        
    @staticmethod
    async def create_user(user: UserCreate):
        try:
            logger.debug(f"Creating user: {user}")
            collection = UserService.get_collection()
            user_dict = user.model_dump()
            result = await collection.insert_one(user_dict)
            created_user = await collection.find_one({"_id": result.inserted_id})
            logger.debug(f"Created user: {created_user}")
            return UserResponse.model_validate(created_user)
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

    @staticmethod
    async def get_user(user_id: str):
        try:
            logger.debug(f"Fetching user by ID: {user_id}")
            collection = UserService.get_collection()
            user = await collection.find_one({"_id": ObjectId(user_id)})
            if user:
                logger.debug(f"User found: {user}")
                return UserResponse.model_validate(user)
            logger.debug("User not found")
            return None
        except InvalidId as e:
            logger.error(f"Invalid ObjectId: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error fetching user: {str(e)}")
            raise

    @staticmethod
    async def update_user(user_id: str, user: UserCreate):
        try:
            logger.debug(f"Updating user ID: {user_id} with data: {user}")
            collection = UserService.get_collection()
            user_dict = user.model_dump()
            result = await collection.update_one(
                {"_id": ObjectId(user_id)}, {"$set": user_dict}
            )
            if result.modified_count == 0:
                logger.debug("No user updated, user not found")
                return None
            updated_user = await UserService.get_user(user_id)
            logger.debug(f"Updated user: {updated_user}")
            return updated_user
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise

    @staticmethod
    async def delete_user(user_id: str):
        try:
            logger.debug(f"Deleting user by ID: {user_id}")
            collection = UserService.get_collection()
            result = await collection.delete_one({"_id": ObjectId(user_id)})
            if result.deleted_count > 0:
                logger.debug(f"Deleted user ID: {user_id}")
                return True
            logger.debug("User not found")
            return False
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise
