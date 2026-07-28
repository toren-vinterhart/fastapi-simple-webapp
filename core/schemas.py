from pydantic import BaseModel, Field, field_validator, field_serializer


class BasePersonSchema(BaseModel):
    name: str = Field(..., description="Enter Persons name")

    @field_validator("name")
    def validate_name(cls, value):
        if len(value) > 32:
            raise ValueError("Name must not exceed 32 characters")
        if not value.isalpha():
            raise ValueError("Name must contain only alphabetic characters")
        return value

    @field_serializer("name")
    def serialize_name(value):
        return value.title()


class PersonCreateSchema(BasePersonSchema):
    pass


class PersonResponseSchema(BasePersonSchema):
    id: int = Field(..., description="Unique user identifier")


class PersonUpdateSchema(BasePersonSchema):
    pass
