from typing import TypeVar, Generic, List, Optional, Any
from pydantic import BaseModel, Field

# Generic type for the items in the paginated list
T = TypeVar('T')

class PaginationInfo(BaseModel):
    """Holds pagination cursor information."""
    next_cursor: Optional[str] = None
    # Acunetix might also include count, total, etc.
    count: Optional[int] = None
    total: Optional[int] = None 

class PaginatedList(BaseModel, Generic[T]):
    """Generic model for representing a paginated list of resources."""
    items: List[T] = Field(..., description="The list of items on the current page.")
    pagination: PaginationInfo = Field(..., description="Pagination details.") 