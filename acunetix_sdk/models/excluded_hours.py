from typing import Optional, List
from pydantic import BaseModel, Field, constr

class ExcludedHoursProfile(BaseModel):
    """
    Corresponds to #/definitions/ExcludedHoursProfile in API spec.
    """
    name: constr(min_length=1, max_length=256) = Field(...)
    excluded_hours_id: Optional[str] = Field(None, description="UUID, read-only for GET")
    time_offset: Optional[int] = Field(default=0, ge=-720, le=840, description="Time offset in minutes")
    # exclusion_matrix is an array of 168 booleans (7 days * 24 hours)
    exclusion_matrix: List[bool] = Field(..., min_length=168, max_length=168, description="Exclusion matrix 7d*24h, true=exclude")

class ExcludedHoursProfilesList(BaseModel):
    """
    Corresponds to #/definitions/ExcludedHoursProfilesList in API spec.
    """
    values: Optional[List[ExcludedHoursProfile]] = Field(default_factory=list)

# Note: API spec for GET /excluded_hours_profiles does not show pagination.
# If it were paginated, we'd use PaginatedList[ExcludedHoursProfile].
