from fastapi import APIRouter, HTTPException, Query
from services.accessibility_service import AccessibilityService
from services.building_service import BuildingService
from services.aggregation_service import AggregationService
from models.building_model import BuildingResponse
from typing import Dict, List, Any, Optional, Union
import logging
from openai import OpenAI
import asyncio
from core.config import settings
import json

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_openai_client():
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def calculate_accessibility_score(rating: List[int]) -> float:
    if rating[1] == 0:  # Avoid division by zero
        return 0
    return (rating[0] / (rating[1] * 5)) * 100  # Convert to percentage


def check_accessibility(aggregation: Dict[str, Any], categories: List[str]) -> bool:
    for category in categories:
        rating_key = f"{category}_rating"
        if rating_key in aggregation:
            score = calculate_accessibility_score(aggregation[rating_key])
            logger.debug(f"Category: {category}, Score: {score}")
            if score < 66:
                return False
        else:
            logger.warning(f"Category {rating_key} not found in aggregation data")
            return False
    return True


# Category functions
def get_entertainment():
    return {
        "category": "Entertainment",
        "description": "Options for fun activities like movies, concerts, or other events.",
    }


def get_establishment():
    return {
        "category": "Establishment",
        "description": "Study places or educational establishments. Here the user can study or work.",
    }


def get_fitness():
    return {
        "category": "Fitness",
        "description": "Fitness-related locations like gyms or sports facilities.",
    }


def get_housing():
    return {"category": "Housing", "description": "Housing-related locations."}


def get_restaurant():
    return {
        "category": "Restaurant",
        "description": "Food-related locations for eating out.",
    }


def get_other():
    return {
        "category": "Other",
        "description": "Other types of locations not covered by the specific categories.",
    }


async def filter_buildings_by_category(
    buildings: List[Any], categories: List[str]
) -> List[Any]:
    filtered_buildings = []
    for building in buildings:
        # Assuming 'category' is the correct attribute. Adjust if needed.
        if hasattr(building, "category") and any(
            category.lower() in building.category.lower() for category in categories
        ):
            filtered_buildings.append(building)
    return filtered_buildings


async def create_sources_list(
    buildings: List[Any], activity_categories: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    sources = []
    for category in activity_categories:
        category_buildings = [
            b
            for b in buildings
            if hasattr(b, "category")
            and category["category"].lower() in b.category.lower()
        ]
        sources.append(
            {
                "category": category["category"],
                "explanation": category["explanation"],
                "buildings": category_buildings,
            }
        )
    return sources


async def plan_weekend_activities(user_input: str) -> List[Dict[str, str]]:
    weekend_activities = [
        {
            "category": "Restaurant",
            "description": "Brunch location",
            "explanation": "Start the day with a leisurely brunch.",
        },
        {
            "category": "Entertainment",
            "description": "Fun activity",
            "explanation": "Enjoy some entertainment in the afternoon.",
        },
        {
            "category": "Establishment",
            "description": "Study or work location",
            "explanation": "Allocate some time for studying or working.",
        },
        {
            "category": "Restaurant",
            "description": "Dinner location",
            "explanation": "End the day with a nice dinner.",
        },
    ]
    return weekend_activities


async def normal_analyze_user_input(user_input: str) -> List[Dict[str, str]]:
    # Existing implementation
    if "weekend" in user_input.lower() and "plan my day" in user_input.lower():
        return await plan_weekend_activities(user_input)
    else:
        # Call the existing OpenAI-based analysis
        return await normal_analyze_user_input(user_input)


@router.post("/comprehensive-plan/{email}")
async def comprehensive_plan(email: str, user_input: str):
    try:
        # Step 1: Plan activities
        user_accessibility_info = (
            await AccessibilityService.get_user_accessibility_categories(email)
        )
        user_disabilities = user_accessibility_info["user_disabilities"]
        building_categories = user_accessibility_info["building_categories"]

        suggested_activities = await normal_analyze_user_input(user_input)
        plan = {
            "user_input": user_input,
            "user_disabilities": user_disabilities,
            "building_categories": building_categories,
            "suggested_activity_categories": suggested_activities,
        }

        # Step 2: Get accessible buildings
        disability_categories = [
            f"{disability}_accessibility" for disability in user_disabilities.keys()
        ]
        accessible_buildings_result = await get_accessible_buildings_from_aggregation(
            disability_categories
        )
        accessible_buildings = accessible_buildings_result.get("buildings", [])

        # Step 3: Filter buildings by suggested activity categories
        suggested_categories = [cat["category"] for cat in suggested_activities]
        filtered_buildings = await filter_buildings_by_category(
            accessible_buildings, suggested_categories
        )

        # Step 4: Create sources list
        sources = await create_sources_list(filtered_buildings, suggested_activities)

        # Prepare the final response
        response = {
            "user_input": user_input,
            "user_disabilities": user_disabilities,
            "suggested_activities": suggested_activities,
            "accessible_buildings": filtered_buildings,
            "sources_for_llm": sources,
        }

        logger.info(f"Comprehensive plan created for user {email}")
        return response

    except Exception as e:
        logger.error(
            f"Error creating comprehensive plan for {email}: {str(e)}", exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


functions = [
    {
        "name": "get_multiple_categories",
        "description": "Get multiple categories based on the user's input, with explanations",
        "parameters": {
            "type": "object",
            "properties": {
                "categories": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "enum": [
                                    "Entertainment",
                                    "Establishment",
                                    "Fitness",
                                    "Housing",
                                    "Restaurant",
                                    "Other",
                                ],
                            },
                            "explanation": {
                                "type": "string",
                                "description": "Explanation of why this category was chosen",
                            },
                        },
                        "required": ["category", "explanation"],
                    },
                    "description": "List of categories that match the user's input, with explanations",
                }
            },
            "required": ["categories"],
        },
    }
]


import json


async def normal_analyze_user_input(user_input: str) -> List[Dict[str, str]]:
    try:
        client = await get_openai_client()
        # logger.debug(f"OpenAI client created successfully")

        response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4 for better understanding
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful assistant that analyzes user input to determine which categories of activities they're interested in. You can suggest multiple categories if the input implies multiple activities. Here are the categories and their meanings:

- Entertainment: Fun activities like movies, concerts, or other events.
- Establishment: Study places, educational establishments, or work locations. This includes any activity related to studying, working, or learning.
- Fitness: Fitness-related locations like gyms or sports facilities.
- Housing: Housing-related locations or activities.
- Restaurant: Food-related locations for eating out or any activity related to dining.
- Other: Other types of locations or activities not covered by the specific categories above.

Please categorize the user's input and provide a brief explanation for each category chosen.""",
                },
                {"role": "user", "content": user_input},
            ],
            functions=functions,
            function_call={"name": "get_multiple_categories"},
        )
        # logger.debug(f"OpenAI API response received: {response}")

        function_calls = response.choices[0].message.function_call
        if function_calls and function_calls.name == "get_multiple_categories":
            try:
                categories = json.loads(function_calls.arguments)["categories"]
                logger.info(f"Categories determined: {categories}")
                return categories
            except json.JSONDecodeError:
                logger.error(
                    f"Error decoding JSON from OpenAI response: {function_calls.arguments}"
                )
                return []
            except KeyError:
                logger.error(
                    f"'categories' key not found in OpenAI response: {function_calls.arguments}"
                )
                return []
        else:
            logger.info("No categories were determined by OpenAI")
            return []
    except Exception as e:
        logger.error(f"Error in analyze_user_input: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error analyzing user input: {str(e)}"
        )


# Update the plan_activities function to use these new return values
async def plan_activities(
    user_input: str,
    user_disabilities: Dict[str, List[str]],
    building_categories: List[str],
) -> Dict[str, Any]:
    try:
        categories = await normal_analyze_user_input(user_input)
        activity_categories = [
            {
                **globals()[f"get_{cat['category'].lower()}"](),
                "explanation": cat["explanation"],
            }
            for cat in categories
        ]
        logger.info(f"Activity categories determined: {activity_categories}")

        return {
            "user_input": user_input,
            "user_disabilities": user_disabilities,
            "building_categories": building_categories,
            "suggested_activity_categories": activity_categories,
        }
    except Exception as e:
        logger.error(f"Error in plan_activities: {str(e)}", exc_info=True)
        raise


@router.get("/test-openai")
async def test_openai_connection():
    try:
        client = await get_openai_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, OpenAI!"}],
        )
        return {
            "message": "OpenAI connection successful",
            "response": response.choices[0].message.content,
        }
    except Exception as e:
        logger.error(f"Error connecting to OpenAI: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error connecting to OpenAI: {str(e)}"
        )


@router.post("/plan-activities/{email}")
async def plan_user_activities(email: str, user_input: str):
    try:
        logger.info(f"Planning activities for user: {email}")
        user_accessibility_info = (
            await AccessibilityService.get_user_accessibility_categories(email)
        )
        user_disabilities = user_accessibility_info["user_disabilities"]
        building_categories = user_accessibility_info["building_categories"]

        plan = await plan_activities(user_input, user_disabilities, building_categories)
        logger.info(f"Activity plan created for user {email}: {plan}")
        return plan
    except Exception as e:
        logger.error(f"Error planning activities for {email}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


async def get_accessible_buildings_from_aggregation(
    categories: List[str],
) -> Dict[str, Any]:
    try:
        # Fetch all aggregations
        all_aggregations = await AggregationService.get_all_aggregations()

        if not all_aggregations:
            logger.warning("No aggregations found in the database")
            return {
                "buildings": [],
                "debug_info": {
                    "total_buildings": 0,
                    "categories_searched": categories,
                    "buildings_checked": [],
                },
            }

        filtered_building_gids = []
        debug_info = {
            "total_buildings": len(all_aggregations),
            "categories_searched": categories,
            "buildings_checked": [],
        }

        for aggregation in all_aggregations:
            building_info = {
                "id": str(aggregation.get("_id")),
                "GID": aggregation.get("GID"),
                "categories_scores": {},
            }

            is_accessible = check_accessibility(aggregation, categories)

            for category in categories:
                rating_key = f"{category}_rating"
                if rating_key in aggregation:
                    score = calculate_accessibility_score(aggregation[rating_key])
                    building_info["categories_scores"][category] = score
                else:
                    building_info["categories_scores"][category] = "N/A"

            debug_info["buildings_checked"].append(building_info)

            if is_accessible:
                filtered_building_gids.append(aggregation["GID"])

        # Fetch full details for filtered buildings
        filtered_buildings = []
        for gid in filtered_building_gids:
            building = await BuildingService.get_building_by_GID(gid)
            if building:
                filtered_buildings.append(building)
            else:
                logger.warning(f"Building with GID {gid} not found")

        return {"buildings": filtered_buildings, "debug_info": debug_info}
    except Exception as e:
        logger.error(
            f"Error fetching accessible buildings from aggregation: {str(e)}",
            exc_info=True,
        )
        raise


@router.get("/accessible-buildings")
async def get_accessible_buildings(
    user_disabilities: str = Query(
        ...,
        description="Comma-separated list of user disabilities (e.g., mobility,hearing,vision)",
    )
) -> Dict[str, Any]:
    try:
        disabilities = [d.strip() for d in user_disabilities.split(",")]
        categories = [f"{disability}_accessibility" for disability in disabilities]

        if not categories:
            raise HTTPException(status_code=400, detail="No disabilities provided")

        logger.debug(f"Searching for categories: {categories}")

        result = await get_accessible_buildings_from_aggregation(categories)

        if result is None:
            raise HTTPException(
                status_code=500, detail="Failed to fetch accessible buildings"
            )

        buildings = result.get("buildings", [])

        return {
            "buildings": buildings,
            "metadata": {
                "total_buildings_found": len(buildings),
                "categories_searched": categories,
            },
            "debug_info": result.get("debug_info", {}),
        }
    except Exception as e:
        logger.error(f"Error getting accessible buildings: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug-openai/{user_input}")
async def debug_openai_response(user_input: str):
    try:
        client = await get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful assistant that analyzes user input to determine which categories of activities they're interested in. You can suggest multiple categories if the input implies multiple activities. Here are the categories and their meanings:

- Entertainment: Fun activities like movies, concerts, or other events.
- Establishment: Study places, educational establishments, or work locations. This includes any activity related to studying, working, or learning.
- Fitness: Fitness-related locations like gyms or sports facilities.
- Housing: Housing-related locations or activities.
- Restaurant: Food-related locations for eating out or any activity related to dining.
- Other: Other types of locations or activities not covered by the specific categories above.

Please categorize the user's input and provide a brief explanation for each category chosen.""",
                },
                {"role": "user", "content": user_input},
            ],
            functions=functions,
            function_call={"name": "get_multiple_categories"},
        )
        return {
            "message": "OpenAI debug response",
            "response": response.dict(),
        }
    except Exception as e:
        logger.error(f"Error in debug OpenAI response: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error in debug OpenAI response: {str(e)}"
        )


# returning the buildings requried for the user
# @router.get(
#     "/user-accessibility-needs/{email}",
#     response_model=Dict[str, Any],
# )
# async def get_user_accessibility_needs(email: str):
#     try:
#         accessibility_info = (
#             await AccessibilityService.get_user_accessibility_categories(email)
#         )
#         logger.info(f"Accessibility info found for user {email}: {accessibility_info}")
#         return accessibility_info
#     except Exception as e:
#         logger.error(f"Error processing accessibility needs for {email}: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
