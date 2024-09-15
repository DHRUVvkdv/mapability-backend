from pydantic import BaseModel, Field, field_serializer, field_validator
from typing import Dict, Union, Tuple, List, Optional
from bson import ObjectId


class AggregationModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    GID: str
    mobility_accessibility_dict: Dict[str, Tuple[int, int]] = Field(
        default_factory=lambda: {
            "slopedramps": (0, 0),
            "powerassisteddoors": (0, 0),
            "accessiblerestrooms": (0, 0),
            "accessibleseatingareas": (0, 0),
        }
    )
    mobility_accessibility_rating: Tuple[int, int] = Field(default=(0, 0))

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


class AggregationCreate(AggregationModel):
    id: Optional[str] = Field(default=None, exclude=True)


class AggregationResponse(BaseModel):
    id: Union[str, ObjectId] = Field(..., alias="_id")
    GID: str
    mobility_accessibility_dict: Dict[str, Union[Tuple[int, int], List[int]]]
    mobility_accessibility_rating: Union[Tuple[int, int], List[int]]

    @field_serializer("id")
    def serialize_id(self, id: Union[str, ObjectId]):
        return str(id)

    @field_validator("id", mode="before")
    @classmethod
    def validate_object_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if ObjectId.is_valid(v):
            return str(ObjectId(v))
        raise ValueError("Invalid ObjectId")

    @field_validator("mobility_accessibility_dict")
    @classmethod
    def validate_mobility_dict(cls, v):
        return {k: tuple(v) if isinstance(v, list) else v for k, v in v.items()}

    @field_validator("mobility_accessibility_rating")
    @classmethod
    def validate_mobility_rating(cls, v):
        return tuple(v) if isinstance(v, list) else v

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, tuple: list},
        "from_attributes": True,
    }
