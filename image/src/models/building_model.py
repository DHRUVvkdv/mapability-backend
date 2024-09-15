from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)
from typing import Optional, Dict, Any
from bson import ObjectId


class BuildingModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    buildingName: str
    category: str
    GID: str
    address: str
    latitude: float
    longitude: float

    mobility_accessibility_dict: dict
    mobility_accessibility_rating: int
    mobility_accessibility_text_aggregate: str
    mobility_accessibility_count: int

    cognitive_accessibility_dict: dict
    cognitive_accessibility_rating: int
    cognitive_accessibility_text_aggregate: str
    cognitive_accessibility_count: int

    hearing_accessibility_dict: dict
    hearing_accessibility_rating: int
    hearing_accessibility_text_aggregate: str
    hearing_accessibility_count: int

    vision_accessibility_dict: dict
    vision_accessibility_rating: int
    vision_accessibility_text_aggregate: str
    vision_accessibility_count: int

    bathroom_accessibility_dict: dict
    bathroom_accessibility_rating: int
    bathroom_accessibility_text_aggregate: str
    bathroom_accessibility_count: int

    lgbtq_inclusivity_dict: dict
    lgbtq_inclusivity_rating: int
    lgbtq_inclusivity_text_aggregate: str
    lgbtq_inclusivity_count: int

    sensory_considerations_dict: dict
    sensory_considerations_rating: int
    sensory_considerations_text_aggregate: str
    sensory_considerations_count: int

    overall_inclusivity_dict: dict
    overall_inclusivity_rating: int
    overall_inclusivity_text_aggregate: str
    overall_inclusivity_count: int

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


class BuildingCreate(BaseModel):
    buildingName: str
    category: str
    GID: str
    address: str
    latitude: float
    longitude: float

    mobility_accessibility_dict: dict
    mobility_accessibility_rating: int
    mobility_accessibility_text_aggregate: str
    mobility_accessibility_count: int

    cognitive_accessibility_dict: dict
    cognitive_accessibility_rating: int
    cognitive_accessibility_text_aggregate: str
    cognitive_accessibility_count: int

    hearing_accessibility_dict: dict
    hearing_accessibility_rating: int
    hearing_accessibility_text_aggregate: str
    hearing_accessibility_count: int

    vision_accessibility_dict: dict
    vision_accessibility_rating: int
    vision_accessibility_text_aggregate: str
    vision_accessibility_count: int

    bathroom_accessibility_dict: dict
    bathroom_accessibility_rating: int
    bathroom_accessibility_text_aggregate: str
    bathroom_accessibility_count: int

    lgbtq_inclusivity_dict: dict
    lgbtq_inclusivity_rating: int
    lgbtq_inclusivity_text_aggregate: str
    lgbtq_inclusivity_count: int

    sensory_considerations_dict: dict
    sensory_considerations_rating: int
    sensory_considerations_text_aggregate: str
    sensory_considerations_count: int

    overall_inclusivity_dict: dict
    overall_inclusivity_rating: int
    overall_inclusivity_text_aggregate: str
    overall_inclusivity_count: int


class BuildingUpdate(BaseModel):
    id: str = Field(..., alias="_id")
    buildingName: str
    category: str
    GID: str
    address: str
    latitude: float
    longitude: float

    mobility_accessibility_dict: dict
    mobility_accessibility_rating: int
    mobility_accessibility_text_aggregate: str
    mobility_accessibility_count: int

    cognitive_accessibility_dict: dict
    cognitive_accessibility_rating: int
    cognitive_accessibility_text_aggregate: str
    cognitive_accessibility_count: int

    hearing_accessibility_dict: dict
    hearing_accessibility_rating: int
    hearing_accessibility_text_aggregate: str
    hearing_accessibility_count: int

    vision_accessibility_dict: dict
    vision_accessibility_rating: int
    vision_accessibility_text_aggregate: str
    vision_accessibility_count: int

    bathroom_accessibility_dict: dict
    bathroom_accessibility_rating: int
    bathroom_accessibility_text_aggregate: str
    bathroom_accessibility_count: int

    lgbtq_inclusivity_dict: dict
    lgbtq_inclusivity_rating: int
    lgbtq_inclusivity_text_aggregate: str
    lgbtq_inclusivity_count: int

    sensory_considerations_dict: dict
    sensory_considerations_rating: int
    sensory_considerations_text_aggregate: str
    sensory_considerations_count: int

    overall_inclusivity_dict: dict
    overall_inclusivity_rating: int
    overall_inclusivity_text_aggregate: str
    overall_inclusivity_count: int


class BuildingResponse(BaseModel):
    id: str = Field(..., alias="_id")
    buildingName: str
    category: str
    GID: str
    address: str
    latitude: float
    longitude: float

    mobility_accessibility_dict: Dict[str, Any]
    mobility_accessibility_rating: int
    mobility_accessibility_text_aggregate: str
    mobility_accessibility_count: int

    cognitive_accessibility_dict: Dict[str, Any]
    cognitive_accessibility_rating: int
    cognitive_accessibility_text_aggregate: str
    cognitive_accessibility_count: int

    hearing_accessibility_dict: Dict[str, Any]
    hearing_accessibility_rating: int
    hearing_accessibility_text_aggregate: str
    hearing_accessibility_count: int

    vision_accessibility_dict: Dict[str, Any]
    vision_accessibility_rating: int
    vision_accessibility_text_aggregate: str
    vision_accessibility_count: int

    bathroom_accessibility_dict: Dict[str, Any]
    bathroom_accessibility_rating: int
    bathroom_accessibility_text_aggregate: str
    bathroom_accessibility_count: int

    lgbtq_inclusivity_dict: Dict[str, Any]
    lgbtq_inclusivity_rating: int
    lgbtq_inclusivity_text_aggregate: str
    lgbtq_inclusivity_count: int

    sensory_considerations_dict: Dict[str, Any]
    sensory_considerations_rating: int
    sensory_considerations_text_aggregate: str
    sensory_considerations_count: int

    overall_inclusivity_dict: Dict[str, Any]
    overall_inclusivity_rating: int
    overall_inclusivity_text_aggregate: str
    overall_inclusivity_count: int

    @model_validator(mode="before")
    @classmethod
    def convert_objectid(cls, values):
        if isinstance(values, dict):
            if "_id" in values:
                if isinstance(values["_id"], ObjectId):
                    values["_id"] = str(values["_id"])
                elif isinstance(values["_id"], dict) and "$oid" in values["_id"]:
                    values["_id"] = values["_id"]["$oid"]
                elif isinstance(values["_id"], int):
                    values["_id"] = str(values["_id"])
        elif isinstance(values, int):
            # If the entire input is an integer, we'll assume it's meant to be the _id
            values = {"_id": str(values)}
        return values

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "from_attributes": True,
    }
