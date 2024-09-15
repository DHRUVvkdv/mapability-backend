from bson import ObjectId
from db.mongodb import db
from fastapi import HTTPException
from models.aggregation_model import (
    AggregationModel,
    AggregationCreate,
    AggregationResponse,
)
from models.review_model import ReviewModel
import logging

logger = logging.getLogger(__name__)


class AggregationService:
    @staticmethod
    def get_collection():
        if db.db is None:
            logger.error("Database not initialized")
            raise HTTPException(status_code=500, detail="Database not initialized")
        return db.db.aggregation

    @staticmethod
    def get_reviews_collection():
        if db.db is None:
            logger.error("Database not initialized")
            raise HTTPException(status_code=500, detail="Database not initialized")
        return db.db.reviews

    @staticmethod
    async def get_or_create_aggregation(GID: str):
        collection = AggregationService.get_collection()
        aggregation = await collection.find_one({"GID": GID})
        if not aggregation:
            new_aggregation = AggregationCreate(GID=GID)
            result = await collection.insert_one(
                new_aggregation.model_dump(exclude_none=True)
            )
            aggregation = await collection.find_one({"_id": result.inserted_id})
        return AggregationModel.model_validate(aggregation)

    @staticmethod
    async def update_aggregation(GID: str):
        reviews_collection = AggregationService.get_reviews_collection()
        aggregation_collection = AggregationService.get_collection()

        aggregation = await AggregationService.get_or_create_aggregation(GID)

        reviews = await reviews_collection.find({"GID": GID}).to_list(length=None)

        mobility_dict = {
            k: [0, 0] for k in aggregation.mobility_accessibility_dict.keys()
        }
        mobility_rating_sum = 0
        mobility_rating_count = 0

        for review in reviews:
            review_model = ReviewModel.model_validate(review)

            if review_model.mobility_accessibility_dict:
                for key, value in review_model.mobility_accessibility_dict.items():
                    if value.lower() in ["true", "false"]:
                        mobility_dict[key][0] += 1 if value.lower() == "true" else 0
                        mobility_dict[key][1] += 1

            if review_model.mobility_accessibility_rating is not 0:
                mobility_rating_sum += review_model.mobility_accessibility_rating
                mobility_rating_count += 1

        aggregation.mobility_accessibility_dict = {
            k: tuple(v) for k, v in mobility_dict.items()
        }
        aggregation.mobility_accessibility_rating = (
            mobility_rating_sum,
            mobility_rating_count,
        )

        await aggregation_collection.update_one(
            {"GID": GID}, {"$set": aggregation.model_dump(exclude_none=True)}
        )

        return aggregation

    @staticmethod
    async def get_aggregation(GID: str):
        collection = AggregationService.get_collection()
        aggregation = await collection.find_one({"GID": GID})
        if not aggregation:
            raise HTTPException(
                status_code=404, detail=f"Aggregation not found for GID: {GID}"
            )
        return AggregationResponse.model_validate(aggregation)

    @staticmethod
    async def debug_update_aggregation(GID: str):
        reviews_collection = AggregationService.get_reviews_collection()
        aggregation_collection = AggregationService.get_collection()

        aggregation = await AggregationService.get_or_create_aggregation(GID)

        reviews = await reviews_collection.find({"GID": GID}).to_list(length=None)

        mobility_dict = {
            k: [0, 0] for k in aggregation.mobility_accessibility_dict.keys()
        }
        mobility_rating_sum = 0
        mobility_rating_count = 0

        for review in reviews:
            review_model = ReviewModel.model_validate(review)

            if review_model.mobility_accessibility_dict:
                for key, value in review_model.mobility_accessibility_dict.items():
                    if value.lower() in ["true", "false"]:
                        mobility_dict[key][0] += 1 if value.lower() == "true" else 0
                        mobility_dict[key][1] += 1

            if review_model.mobility_accessibility_rating is not None:
                mobility_rating_sum += review_model.mobility_accessibility_rating
                mobility_rating_count += 1

        aggregation.mobility_accessibility_dict = {
            k: tuple(v) for k, v in mobility_dict.items()
        }
        aggregation.mobility_accessibility_rating = (
            mobility_rating_sum,
            mobility_rating_count,
        )

        # Convert the aggregation model to a dictionary
        raw_data = aggregation.model_dump()

        # Log the raw data
        logger.debug(f"Raw aggregation data for GID {GID}: {raw_data}")

        return raw_data
