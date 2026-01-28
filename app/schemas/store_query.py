from pydantic import BaseModel, Field
from typing import Optional

class WishlistQuery(BaseModel):
    limit: Optional[int] = Field(default=50, ge=1, le=200)
    offset: Optional[int] = Field(default=0, ge=0)
