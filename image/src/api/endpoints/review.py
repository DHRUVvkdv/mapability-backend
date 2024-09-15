from fastapi import APIRouter, HTTPException
from services.review_service import ReviewService
from models.review_model import ReviewCreate, ReviewResponse
from pymongo.errors import PyMongoError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/get-reviews", response_model=list[ReviewResponse])
async def get_reviews():
    try:
        return await ReviewService.get_reviews()
    except PyMongoError as e:
        logger.error(f"Database error in get_reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/create-review", response_model=ReviewResponse)
async def create_review(review: ReviewCreate):
    try:
        # # logger.debug(f"Received review create request: {review}")
        result = await ReviewService.create_review(review)
        # # logger.debug(f"Review created successfully: {result}")
        return result
    except PyMongoError as e:
        logger.error(f"Database error in create_review: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in create_review: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
