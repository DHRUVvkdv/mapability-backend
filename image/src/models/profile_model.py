from pydantic import BaseModel, Field, field_serializer, field_validator
from typing import Optional
from bson import ObjectId

class ProfileModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    gender: str
    age: int
    email: str
    user_name: str

    mobility: dict
    cognitive: dict
    hearing: dict
    vision: dict
    LGBTQ: bool
    other: dict

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


class ProfileCreate(BaseModel):
    gender: str
    age: int
    email: str
    user_name: str

    mobility: dict
    cognitive: dict
    hearing: dict
    vision: dict
    LGBTQ: bool
    other: dict

class ProfileUpdate(BaseModel):
    id: str = Field(..., alias="_id")
    gender: str
    age: int
    email: str
    user_name: str

    mobility: dict
    cognitive: dict
    hearing: dict
    vision: dict
    LGBTQ: bool
    other: dict


class ProfileResponse(ProfileModel):
    id: str = Field(..., alias="_id")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "from_attributes": True,
    }
