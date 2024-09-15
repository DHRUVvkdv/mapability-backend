from fastapi import APIRouter, HTTPException
from services.accessibility_service import AccessibilityService
from typing import Dict, List, Union
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/user-accessibility-needs/{email}",
    response_model=Union[Dict[str, List[str]], Dict[str, str]],
)
async def get_user_accessibility_needs(email: str):
    try:
        accessibility_needs = await AccessibilityService.get_user_accessibility_needs(
            email
        )
        if not accessibility_needs:
            logger.info(f"No accessibility needs found for user: {email}")
            return {"message": "User has no specific accessibility needs."}
        logger.info(
            f"Accessibility needs found for user {email}: {accessibility_needs}"
        )
        return accessibility_needs
    except Exception as e:
        logger.error(f"Error processing accessibility needs for {email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# TODO: Add more endpoints for planning functionality
# For example:
# @router.post("/plan-day")
# async def plan_day(email: str, activities: List[str]):
#     # Implement day planning logic here
#     pass
