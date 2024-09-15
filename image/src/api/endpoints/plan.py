from fastapi import APIRouter, HTTPException
from services.accessibility_service import AccessibilityService
from typing import Dict, List, Any
import logging
from openai import OpenAI
import asyncio
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_openai_client():
    return OpenAI(api_key=settings.OPENAI_API_KEY)


# Category functions
def get_entertainment():
    return "Entertainment"


def get_establishment():
    return "Establishment"  # Note: This is interpreted as a study place


def get_fitness():
    return "Fitness"


def get_housing():
    return "Housing"


def get_restaurant():
    return "Restaurant"


def get_other():
    return "Other"


functions = [
    {
        "name": "get_entertainment",
        "description": "Get entertainment options for activities like movies, concerts, or other fun events.",
    },
    {
        "name": "get_establishment",
        "description": "Get study places or educational establishments.",
    },
    {
        "name": "get_fitness",
        "description": "Get fitness-related locations like gyms or sports facilities.",
    },
    {
        "name": "get_housing",
        "description": "Get housing-related locations.",
    },
    {
        "name": "get_restaurant",
        "description": "Get restaurant or food-related locations. If the users mentions about eating or something similar, this function will be called.",
    },
    {
        "name": "get_other",
        "description": "Get other types of locations not covered by the specific categories.",
    },
]


async def analyze_user_input(user_input: str) -> List[str]:
    try:
        client = await get_openai_client()
        logger.debug(f"OpenAI client created successfully")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that analyzes user input to determine which categories of activities they're interested in.",
                },
                {"role": "user", "content": user_input},
            ],
            functions=functions,
            function_call="auto",
        )
        logger.debug(f"OpenAI API response received: {response}")

        function_calls = response.choices[0].message.function_call
        if function_calls:
            function_name = function_calls.name
            logger.info(f"Function called: {function_name}")
            return [globals()[function_name]()]
        else:
            logger.info("No function was called by OpenAI")
            return []
    except Exception as e:
        logger.error(f"Error in analyze_user_input: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error analyzing user input: {str(e)}"
        )


async def plan_activities(
    user_input: str,
    user_disabilities: Dict[str, List[str]],
    building_categories: List[str],
) -> Dict[str, Any]:
    try:
        activity_categories = await analyze_user_input(user_input)
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
