from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from services.building_service import BuildingService
from models.building_model import BuildingCreate, BuildingResponse, BuildingUpdate
from pymongo.errors import PyMongoError
from bson.errors import InvalidId
import json
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


@router.get("/get-raw-buildings")
async def get_raw_buildings():
    try:
        raw_buildings = await BuildingService.get_raw_buildings()
        return JSONResponse(
            content=json.loads(json.dumps(raw_buildings, cls=JSONEncoder))
        )
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/{GoogleID}", response_model=BuildingResponse)
async def get_building_by_name(GoogleID: str):
    try:
        building = await BuildingService.get_building_by_GID(GoogleID)
        if building is None:
            return -1
        return building
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid profile ID format")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/get-buildings/get", response_model=list[BuildingResponse])
async def get_buildings():
    try:
        collection = BuildingService.get_collection()
        cursor = collection.find()
        buildings = await cursor.to_list(length=None)

        # # logger.debug(f"Raw buildings data: {buildings}")

        if not buildings:
            logger.info("No buildings found")
            return []

        validated_buildings = []
        for building in buildings:
            try:
                building["_id"] = str(building["_id"])  # Convert ObjectId to string
                validated_building = BuildingResponse.model_validate(building)
                validated_buildings.append(validated_building)
            except Exception as e:
                logger.error(
                    f"Validation error for building {building.get('_id', 'unknown')}: {str(e)}"
                )

        logger.info(f"Returning {len(validated_buildings)} validated buildings")
        return validated_buildings
    except Exception as e:
        logger.error(f"Error fetching buildings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/create-building", response_model=BuildingResponse)
async def create_building(building: BuildingCreate):
    try:
        return await BuildingService.create_building(building)
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/update-building", response_model=BuildingResponse)
async def update_building(building: BuildingUpdate):
    try:
        return await BuildingService.update_building(building)
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
