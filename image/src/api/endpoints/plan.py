from fastapi import APIRouter, HTTPException
from services.accessibility_service import AccessibilityService
from typing import Dict, List, Any
import logging
from openai import OpenAI
import asyncio
from core.config import settings
import json

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_openai_client():
    return OpenAI(api_key=settings.OPENAI_API_KEY)


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


async def analyze_user_input(user_input: str) -> List[Dict[str, str]]:
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
        categories = await analyze_user_input(user_input)
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
