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
from typing import Dict, List, Tuple
from openai import OpenAI
from core.config import settings

logger = logging.getLogger(__name__)


async def get_openai_client():
    return OpenAI(api_key=settings.OPENAI_API_KEY)


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

    @staticmethod
    async def summarize_building(GID: str) -> Dict[str, str]:
        aggregation = await AggregationService.get_aggregation(GID)
        summary = {}

        categories = [
            "mobility_accessibility",
            "cognitive_accessibility",
            "hearing_accessibility",
            "vision_accessibility",
            "bathroom_accessibility",
            "lgbtq_inclusivity",
            "sensory_considerations",
            "overall_inclusivity",
        ]

        category_intros = {
            "mobility_accessibility": "Mobility features and accessibility:",
            "cognitive_accessibility": "Cognitive support and accessibility:",
            "hearing_accessibility": "Hearing assistance and accessibility:",
            "vision_accessibility": "Vision support and accessibility:",
            "bathroom_accessibility": "Bathroom accessibility features:",
            "lgbtq_inclusivity": "LGBTQ+ inclusivity measures:",
            "sensory_considerations": "Sensory-friendly accommodations:",
            "overall_inclusivity": "Overall inclusivity assessment:",
        }

        def process_dict(category_dict: Dict[str, List[int]]) -> List[str]:
            results = []
            for key, value in category_dict.items():
                if value[1] > 0:  # If there are any ratings
                    percentage = (value[0] / value[1]) * 100
                    status = "Available" if percentage >= 50 else "Limited"
                    results.append(f"- {key.replace('_', ' ').title()}: {status}")
            return results

        def process_rating(rating: Tuple[int, int]) -> str:
            if rating[1] > 0:
                avg_rating = rating[0] / rating[1]
                return f"{avg_rating:.1f}/5"
            return "No ratings available"

        client = await get_openai_client()

        for category in categories:
            dict_field = f"{category}_dict"
            rating_field = f"{category}_rating"
            text_field = f"{category}_texts"

            category_summary = [f"## {category.replace('_', ' ').title()}"]
            category_summary.append(category_intros[category])

            # Process dictionary data
            if hasattr(aggregation, dict_field):
                category_dict = getattr(aggregation, dict_field)
                feature_summary = process_dict(category_dict)
                if feature_summary:
                    category_summary.append("\nFeatures:")
                    category_summary.extend(feature_summary)
                else:
                    category_summary.append("\nNo specific features reported.")

            # Process rating
            if hasattr(aggregation, rating_field):
                rating = getattr(aggregation, rating_field)
                category_summary.append(f"\nAverage rating: {process_rating(rating)}")

            # Process text reviews
            if hasattr(aggregation, text_field):
                texts = getattr(aggregation, text_field)
                if texts:
                    full_text = "\n".join(texts)
                    prompt = f". Disregard all numeric fields, don't apply any formatting. Only provide a summary of the reviews that aims to provide readers a quick understanding of that accessibility field for the building. Summarize the following accessibility reviews for {category.replace('_', ' ')} in 1-2 sentences, highlighting key points and areas for improvement:\n\n{full_text}"

                    try:
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a helpful assistant summarizing accessibility reviews.",
                                },
                                {"role": "user", "content": prompt},
                            ],
                        )
                        summary_text = response.choices[0].message.content
                        category_summary.append(
                            f"\nUser feedback summary: {summary_text}"
                        )
                    except Exception as e:
                        logger.error(f"Error in OpenAI summarization: {str(e)}")
                        category_summary.append("\nError in summarizing user comments.")
                else:
                    category_summary.append(
                        "\nNo user comments available for this category."
                    )

            summary[category.replace("_", " ").title()] = "\n".join(category_summary)

        return summary
