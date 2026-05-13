from typing import Optional

from pydantic import BaseModel, Field


class DetailsExtractor(BaseModel):
    name: Optional[str] = Field(default=None, description="Name of the user")
    age: Optional[int] = Field(default=None, description="age of the user")
