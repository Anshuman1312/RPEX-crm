from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

import uuid


class DepartmentResponse(BaseModel):
    """Department response."""

    id: uuid.UUID
    name: str
    code: str
    parent_id: Optional[uuid.UUID] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DesignationResponse(BaseModel):
    """Designation response."""

    id: uuid.UUID
    name: str
    code: str
    level: int
    is_active: bool
    department_id: uuid.UUID
    department: Optional[DepartmentResponse] = None
    created_at: datetime

    model_config = {"from_attributes": True}
