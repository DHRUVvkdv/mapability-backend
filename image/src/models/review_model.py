from pydantic import BaseModel, Field, field_serializer, field_validator
from typing import Optional
from bson import ObjectId


class ReviewModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    buildingName: Optional[str] = None
    category: Optional[str] = None
    GID: Optional[str] = None
    user_name: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    mobility_accessibility_dict: Optional[dict] = None
    mobility_accessibility_rating: Optional[int] = None
    mobility_accessibility_text: Optional[str] = None

    cognitive_accessibility_dict: Optional[dict] = None
    cognitive_accessibility_rating: Optional[int] = None
    cognitive_accessibility_text: Optional[str] = None

    hearing_accessibility_dict: Optional[dict] = None
    hearing_accessibility_rating: Optional[int] = None
    hearing_accessibility_text: Optional[str] = None

    vision_accessibility_dict: Optional[dict] = None
    vision_accessibility_rating: Optional[int] = None
    vision_accessibility_text: Optional[str] = None

    bathroom_accessibility_dict: Optional[dict] = None
    bathroom_accessibility_rating: Optional[int] = None
    bathroom_accessibility_text: Optional[str] = None

    lgbtq_inclusivity_dict: Optional[dict] = None
    lgbtq_inclusivity_rating: Optional[int] = None
    lgbtq_inclusivity_text: Optional[str] = None

    sensory_considerations_dict: Optional[dict] = None
    sensory_considerations_rating: Optional[int] = None
    sensory_considerations_text: Optional[str] = None

    overall_inclusivity_dict: Optional[dict] = None
    overall_inclusivity_rating: Optional[int] = None
    overall_inclusivity_text: Optional[str] = None

    # Add any additional fields that might be in your database
    comment: Optional[str] = None

    @field_serializer("id")
    def serialize_id(self, id: Optional[str], _info):
        return str(id) if id else None

    @field_validator("id", mode="before")
    @classmethod
    def validate_object_id(cls, v):
        if v is None:
            return None
        if isinstance(v, ObjectId):
            return str(v)
        if ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "from_attributes": True,
    }


class ReviewCreate(ReviewModel):
    id: Optional[str] = Field(default=None, exclude=True)


class ReviewResponse(ReviewModel):
    id: str = Field(..., alias="_id")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "from_attributes": True,
    }
