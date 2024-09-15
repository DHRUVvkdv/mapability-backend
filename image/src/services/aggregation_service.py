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

        # Get all reviews for this GID
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

        # Reset all counts and ratings
        for category in accessibility_categories:
            dict_field = f"{category}_dict"
            rating_field = f"{category}_rating"
            text_field = f"{category}_texts"

            category_dict = getattr(aggregation, dict_field)
            for key in category_dict:
                category_dict[key] = (0, 0)  # Reset counts
            setattr(aggregation, dict_field, category_dict)
            setattr(aggregation, rating_field, (0, 0))  # Reset rating
            setattr(aggregation, text_field, [])  # Reset texts

        # Process all reviews
        for review in reviews:
            review_model = ReviewModel.model_validate(review)

            for category in accessibility_categories:
                dict_field = f"{category}_dict"
                rating_field = f"{category}_rating"
                text_field = f"{category}_texts"

                category_dict = getattr(aggregation, dict_field)
                category_rating_sum, category_rating_count = getattr(
                    aggregation, rating_field
                )
                category_texts = getattr(aggregation, text_field)

                if hasattr(review_model, dict_field):
                    review_dict = getattr(review_model, dict_field)
                    if review_dict:
                        for key, value in review_dict.items():
                            if key in category_dict:
                                true_count, total_count = category_dict[key]
                                if value.lower() in ["true", "false"]:
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

                if hasattr(
                    review_model, text_field.rstrip("s")
                ):  # Remove 's' from 'texts'
                    text = getattr(review_model, text_field.rstrip("s"))
                    if text and text.strip():  # Only add non-empty texts
                        category_texts.append(text.strip())

                setattr(aggregation, dict_field, category_dict)
                setattr(
                    aggregation,
                    rating_field,
                    (category_rating_sum, category_rating_count),
                )
                setattr(aggregation, text_field, category_texts)

        # Update the aggregation in the database
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

    @staticmethod
    async def get_all_aggregations():
        try:
            collection = AggregationService.get_collection()
            aggregations = await collection.find({}).to_list(None)
            return aggregations
        except Exception as e:
            logger.error(f"Error fetching all aggregations: {str(e)}", exc_info=True)
            raise
