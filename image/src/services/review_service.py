from bson import ObjectId
from db.mongodb import db
from fastapi import HTTPException
from models.review_model import ReviewModel, ReviewCreate, ReviewResponse
import logging

logger = logging.getLogger(__name__)


class ReviewService:
    @staticmethod
    def get_collection():
        if db.db is None:
            logger.error("Database not initialized")
            raise HTTPException(status_code=500, detail="Database not initialized")
        return db.db.reviews

    @staticmethod
    async def get_reviews():
        try:
            logger.debug("Fetching all reviews")
            collection = ReviewService.get_collection()
            reviews = await collection.find().to_list(1000)
            logger.debug(f"Fetched reviews: {reviews}")
            return [ReviewResponse.model_validate(review) for review in reviews]
        except Exception as e:
            logger.error(f"Error fetching reviews: {str(e)}")
            raise

    @staticmethod
    async def create_review(review: ReviewCreate):
        try:
            logger.debug(f"Creating review: {review}")
            collection = ReviewService.get_collection()

            logger.debug("Converting review to dict")
            review_dict = review.model_dump(exclude_none=True)
            logger.debug(f"Review dict: {review_dict}")

            logger.debug("Inserting review into database")
            result = await collection.insert_one(review_dict)
            logger.debug(f"Insert result: {result.inserted_id}")

            created_review = await collection.find_one({"_id": result.inserted_id})
            logger.debug(f"Created review: {created_review}")

            return ReviewResponse.model_validate(created_review)
        except Exception as e:
            logger.error(f"Error creating review: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
