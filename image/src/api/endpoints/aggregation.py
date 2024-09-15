from fastapi import APIRouter, HTTPException
from services.aggregation_service import AggregationService
from models.aggregation_model import AggregationResponse
from pymongo.errors import PyMongoError
import logging
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/get-aggregation/{GID}", response_model=AggregationResponse)
async def get_aggregation(GID: str):
    try:
        return await AggregationService.get_aggregation(GID)
    except PyMongoError as e:
        logger.error(f"Database error in get_aggregation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_aggregation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/update-aggregation/{GID}", response_model=AggregationResponse)
async def update_aggregation(GID: str):
    try:
        return await AggregationService.update_aggregation(GID)
    except PyMongoError as e:
        logger.error(f"Database error in update_aggregation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in update_aggregation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/debug-update-aggregation/{GID}")
async def debug_update_aggregation(GID: str):
    try:
        # Call the update_aggregation method from the service
        raw_data = await AggregationService.debug_update_aggregation(GID)

        # Log the raw data
        logger.debug(f"Raw aggregation data for GID {GID}: {raw_data}")

        # Return the raw data as JSON
        return JSONResponse(content=raw_data)
    except PyMongoError as e:
        logger.error(f"Database error in debug_update_aggregation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(
            f"Unexpected error in debug_update_aggregation: {str(e)}", exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
