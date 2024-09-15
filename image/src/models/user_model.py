from pydantic import BaseModel, Field, field_serializer, field_validator
from typing import Optional
from bson import ObjectId

class UserModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_name: str
    email: str
    password: str


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


class UserCreate(BaseModel):
    user_name: str
    email: str
    password: str


class UserResponse(UserModel):
    id: str = Field(..., alias="_id")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "from_attributes": True,
    }
