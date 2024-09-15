from services.profile_service import ProfileService
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class AccessibilityService:
    @staticmethod
    async def get_user_accessibility_needs(email: str) -> Dict[str, List[str]]:
        try:
            profile = await ProfileService.get_profile_by_email(email)
            if not profile:
                # #logger.debug(f"No profile found for email: {email}")
                return {}

            # #logger.debug(f"Raw profile data: {profile}")

            user_accessibility_needs = {}
            for category in ["mobility", "cognitive", "hearing", "vision", "other"]:
                if hasattr(profile, category):
                    category_data = getattr(profile, category)
                    # #logger.debug(f"Category {category} data: {category_data}")
                    needs = [key for key, value in category_data.items() if value]
                    if needs:
                        user_accessibility_needs[category] = needs

            if hasattr(profile, "LGBTQ") and profile.LGBTQ:
                user_accessibility_needs["LGBTQ"] = ["LGBTQ"]

            # #logger.debug(
            #     f"Processed accessibility needs for {email}: {user_accessibility_needs}"
            # )

            if not user_accessibility_needs:
                logger.info(f"No accessibility needs found for user: {email}")

            return user_accessibility_needs
        except Exception as e:
            logger.error(f"Error getting accessibility needs for {email}: {str(e)}")
            raise

    @staticmethod
    def map_disabilities_to_building_categories(
        disabilities: Dict[str, List[str]]
    ) -> List[str]:
        category_mapping = {
            "mobility": "mobility_accessibility",
            "cognitive": "cognitive_accessibility",
            "hearing": "hearing_accessibility",
            "vision": "vision_accessibility",
            "other": ["sensory_considerations", "overall_inclusivity"],
            "LGBTQ": "lgbtq_inclusivity",
        }

        building_categories = set()

        for category, disabilities_list in disabilities.items():
            if disabilities_list:  # Only process non-empty lists
                if category in category_mapping:
                    if isinstance(category_mapping[category], list):
                        building_categories.update(category_mapping[category])
                    else:
                        building_categories.add(category_mapping[category])

        return list(building_categories)

    @staticmethod
    async def get_user_accessibility_categories(email: str) -> Dict[str, Any]:
        try:
            user_disabilities = await AccessibilityService.get_user_accessibility_needs(
                email
            )
            if not user_disabilities:
                logger.info(f"No accessibility needs found for user: {email}")
                return {"message": "NA"}

            building_categories = (
                AccessibilityService.map_disabilities_to_building_categories(
                    user_disabilities
                )
            )

            return {
                "user_disabilities": user_disabilities,
                "building_categories": building_categories,
            }
        except Exception as e:
            logger.error(
                f"Error processing accessibility categories for {email}: {str(e)}"
            )
            raise
