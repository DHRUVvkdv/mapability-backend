from bson import ObjectId
from db.mongodb import db
from fastapi import HTTPException
from models.building_model import (
    BuildingModel,
    BuildingCreate,
    BuildingResponse,
    BuildingUpdate,
)
import logging

logger = logging.getLogger(__name__)


class BuildingService:
    @staticmethod
    def get_collection():
        if db.db is None:
            logger.error("Database not initialized")
            raise HTTPException(status_code=500, detail="Database not initialized")
        return db.db.buildings

    @staticmethod
    async def get_building_by_name(buildingName: str):
        try:
            logger.debug(f"Fetching building by name: {buildingName}")
            collection = BuildingService.get_collection()
            building = await collection.find_one({"buildingName": buildingName})
            if building:
                logger.debug(f"Building found: {building}")
                return BuildingResponse.model_validate(building)
            logger.debug("Building not found")
            return None
        except Exception as e:
            logger.error(f"Error fetching building by name: {str(e)}")
            raise

    @staticmethod
    async def get_building_by_GID(GID: str):
        try:
            logger.debug(f"Fetching building by GID: {GID}")
            collection = BuildingService.get_collection()
            building = await collection.find_one({"GID": GID})
            if building:
                logger.debug(f"Building found: {building}")
                building["_id"] = str(building["_id"])  # Convert ObjectId to string
                return BuildingResponse.model_validate(building)
            logger.debug("Building not found")
            return None
        except Exception as e:
            logger.error(f"Error fetching building by GID: {str(e)}")
            raise

    @staticmethod
    async def get_buildings():
        GID = "66e60e28dafccfa65d64ac7e"
        try:
            logger.debug(f"Fetching building by GID: {GID}")
            collection = BuildingService.get_collection()
            building = await collection.find_one({"GID": GID})
            if building:
                logger.debug(f"Building found: {building}")
                building["_id"] = str(building["_id"])  # Convert ObjectId to string
                return BuildingResponse.model_validate(building)
            logger.debug("Building not found")
            return None
        except Exception as e:
            logger.error(f"Error fetching building by GID: {str(e)}")
            raise

    @staticmethod
    async def get_raw_buildings():
        try:
            collection = BuildingService.get_collection()
            buildings = await collection.find().to_list(1000)
            return buildings
        except Exception as e:
            print(f"Error fetching raw buildings: {str(e)}")
            raise

    @staticmethod
    async def create_building(building: BuildingCreate):
        try:
            logger.debug(f"Creating building: {building}")
            collection = BuildingService.get_collection()
            building_dict = building.model_dump()
            result = await collection.insert_one(building_dict)
            created_building = await collection.find_one({"_id": result.inserted_id})
            logger.debug(f"Created building: {created_building}")
            return BuildingResponse.model_validate(created_building)
        except Exception as e:
            logger.error(f"Error creating building: {str(e)}")
            raise

    @staticmethod
    async def update_building(building: BuildingUpdate):
        try:
            logger.debug(f"Update building: {building}")
            collection = BuildingService.get_collection()
            building_dict = building.model_dump()
            update_result = await collection.update_one(
                {"_id": ObjectId(building_dict["id"])}, {"$set": building_dict}
            )
            if update_result.modified_count == 0:
                logger.error("No building was updated.")
                raise HTTPException(status_code=404, detail="Building not found.")
            updated_building = await collection.find_one(
                {"_id": ObjectId(building_dict["id"])}
            )
            logger.debug(f"Update building: {updated_building}")
            return BuildingResponse.model_validate(updated_building)
        except Exception as e:
            logger.error(f"Error updating building: {str(e)}")
            raise
