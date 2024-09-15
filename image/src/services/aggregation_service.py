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

        accessibility_categories = [
            "mobility_accessibility",
            "cognitive_accessibility",
            "hearing_accessibility",
            "vision_accessibility",
            "bathroom_accessibility",
            "lgbtq_inclusivity",
            "sensory_considerations",
            "overall_inclusivity",
        ]

        for category in accessibility_categories:
            dict_field = f"{category}_dict"
            rating_field = f"{category}_rating"

            category_dict = getattr(aggregation, dict_field)
            category_rating_sum, category_rating_count = getattr(
                aggregation, rating_field
            )

            for review in reviews:
                review_model = ReviewModel.model_validate(review)

                if hasattr(review_model, dict_field):
                    review_dict = getattr(review_model, dict_field)
                    if review_dict:
                        for key, value in review_dict.items():
                            if key in category_dict:
                                if value.lower() in ["true", "false"]:
                                    true_count, total_count = category_dict[key]
                                    category_dict[key] = (
                                        true_count
                                        + (1 if value.lower() == "true" else 0),
                                        total_count + 1,
                                    )

                if hasattr(review_model, rating_field):
                    rating = getattr(review_model, rating_field)
                    if rating is not None and rating != 0:
                        category_rating_sum += rating
                        category_rating_count += 1

            setattr(aggregation, dict_field, category_dict)
            setattr(
                aggregation, rating_field, (category_rating_sum, category_rating_count)
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
        aggregation = await AggregationService.update_aggregation(GID)
        raw_data = aggregation.model_dump()
        logger.debug(f"Raw aggregation data for GID {GID}: {raw_data}")
        return raw_data
