from services.profile_service import ProfileService
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class AccessibilityService:
    @staticmethod
    async def get_user_accessibility_needs(email: str) -> Dict[str, List[str]]:
        try:
            profile = await ProfileService.get_profile_by_email(email)
            if not profile:
                logger.debug(f"No profile found for email: {email}")
                return {}

            logger.debug(f"Raw profile data: {profile}")

            user_accessibility_needs = {}
            for category in ["mobility", "cognitive", "hearing", "vision", "other"]:
                if hasattr(profile, category):
                    category_data = getattr(profile, category)
                    logger.debug(f"Category {category} data: {category_data}")
                    needs = [key for key, value in category_data.items() if value]
                    if needs:
                        user_accessibility_needs[category] = needs

            if hasattr(profile, "LGBTQ") and profile.LGBTQ:
                user_accessibility_needs["LGBTQ"] = ["LGBTQ"]

            logger.debug(
                f"Processed accessibility needs for {email}: {user_accessibility_needs}"
            )

            if not user_accessibility_needs:
                logger.info(f"No accessibility needs found for user: {email}")

            return user_accessibility_needs
        except Exception as e:
            logger.error(f"Error getting accessibility needs for {email}: {str(e)}")
            raise
