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
    cognitive_accessibility_dict: Dict[str, Tuple[int, int]] = Field(
        default_factory=lambda: {
            "clearsignage": (0, 0),
            "quietspaces": (0, 0),
            "simplifiedlayout": (0, 0),
            "stafftrainingforcognitivesupport": (0, 0),
        }
    )
    cognitive_accessibility_rating: Tuple[int, int] = Field(default=(0, 0))
    hearing_accessibility_dict: Dict[str, Tuple[int, int]] = Field(
        default_factory=lambda: {
            "visualalarms": (0, 0),
            "hearingloopsystems": (0, 0),
            "signlanguageinterpretersavailable": (0, 0),
            "captioningonmedia": (0, 0),
        }
    )
    hearing_accessibility_rating: Tuple[int, int] = Field(default=(0, 0))
    vision_accessibility_dict: Dict[str, Tuple[int, int]] = Field(
        default_factory=lambda: {
            "braillesignage": (0, 0),
            "audiodescriptions": (0, 0),
            "high-contrastsignage": (0, 0),
            "tactileguidancesystems": (0, 0),
        }
    )
    vision_accessibility_rating: Tuple[int, int] = Field(default=(0, 0))
    bathroom_accessibility_dict: Dict[str, Tuple[int, int]] = Field(
        default_factory=lambda: {
            "gender-neutraloptions": (0, 0),
            "family/companioncarerooms": (0, 0),
            "adultchangingtables": (0, 0),
            "automaticfixtures": (0, 0),
        }
    )
    bathroom_accessibility_rating: Tuple[int, int] = Field(default=(0, 0))
    lgbtq_inclusivity_dict: Dict[str, Tuple[int, int]] = Field(
        default_factory=lambda: {
            "gender-inclusivepolicies": (0, 0),
            "lgbtq+safespacecertified": (0, 0),
            "stafftrainingonlgbtq+issues": (0, 0),
        }
    )
    lgbtq_inclusivity_rating: Tuple[int, int] = Field(default=(0, 0))
    sensory_considerations_dict: Dict[str, Tuple[int, int]] = Field(
        default_factory=lambda: {
            "quiethours/zones": (0, 0),
            "adjustablelighting": (0, 0),
            "scent-freeareas": (0, 0),
        }
    )
    sensory_considerations_rating: Tuple[int, int] = Field(default=(0, 0))
    overall_inclusivity_dict: Dict[str, Tuple[int, int]] = Field(
        default_factory=lambda: {
            "diverserepresentationinimagery/art": (0, 0),
            "inclusivelanguageinsignageandmaterials": (0, 0),
            "culturalsensitivitytrainingforstaff": (0, 0),
        }
    )
    overall_inclusivity_rating: Tuple[int, int] = Field(default=(0, 0))

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
    cognitive_accessibility_dict: Dict[str, Union[Tuple[int, int], List[int]]]
    cognitive_accessibility_rating: Union[Tuple[int, int], List[int]]
    hearing_accessibility_dict: Dict[str, Union[Tuple[int, int], List[int]]]
    hearing_accessibility_rating: Union[Tuple[int, int], List[int]]
    vision_accessibility_dict: Dict[str, Union[Tuple[int, int], List[int]]]
    vision_accessibility_rating: Union[Tuple[int, int], List[int]]
    bathroom_accessibility_dict: Dict[str, Union[Tuple[int, int], List[int]]]
    bathroom_accessibility_rating: Union[Tuple[int, int], List[int]]
    lgbtq_inclusivity_dict: Dict[str, Union[Tuple[int, int], List[int]]]
    lgbtq_inclusivity_rating: Union[Tuple[int, int], List[int]]
    sensory_considerations_dict: Dict[str, Union[Tuple[int, int], List[int]]]
    sensory_considerations_rating: Union[Tuple[int, int], List[int]]
    overall_inclusivity_dict: Dict[str, Union[Tuple[int, int], List[int]]]
    overall_inclusivity_rating: Union[Tuple[int, int], List[int]]

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

    @field_validator(
        "mobility_accessibility_dict",
        "cognitive_accessibility_dict",
        "hearing_accessibility_dict",
        "vision_accessibility_dict",
        "bathroom_accessibility_dict",
        "lgbtq_inclusivity_dict",
        "sensory_considerations_dict",
        "overall_inclusivity_dict",
    )
    @classmethod
    def validate_dict(cls, v):
        return {k: tuple(v) if isinstance(v, list) else v for k, v in v.items()}

    @field_validator(
        "mobility_accessibility_rating",
        "cognitive_accessibility_rating",
        "hearing_accessibility_rating",
        "vision_accessibility_rating",
        "bathroom_accessibility_rating",
        "lgbtq_inclusivity_rating",
        "sensory_considerations_rating",
        "overall_inclusivity_rating",
    )
    @classmethod
    def validate_rating(cls, v):
        return tuple(v) if isinstance(v, list) else v

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, tuple: list},
        "from_attributes": True,
    }
