from pydantic import BaseModel, Field, HttpUrl, field_validator


class Asset(BaseModel):
    asset_id: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=100)
    image_url: str = Field(..., min_length=1, max_length=500)
    total: int = Field(..., gt=0)
    remaining: int = Field(..., ge=0)
    borrowers: list[str] = Field(default_factory=list)


class CreateAssetRequest(BaseModel):
    asset_id: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=100)
    image_url: str | HttpUrl = Field(..., min_length=1, max_length=500)
    total: int = Field(..., gt=0)

    @field_validator("asset_id", "name", mode="before")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        return value


class EmployeeActionRequest(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=64)

    @field_validator("employee_id", mode="before")
    @classmethod
    def strip_employee_id(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        return value


class HealthResponse(BaseModel):
    status: str
    asset_count: int
