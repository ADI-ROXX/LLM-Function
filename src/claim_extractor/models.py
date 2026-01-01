from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ClaimType(str, Enum):
    EXPLICIT = "explicit"
    IMPLICIT = "implicit"
    CONDITIONAL = "conditional"
    VAGUE = "vague"


class Claim(BaseModel):
    claim_text: str
    action_verb: Optional[str] = None
    target_object: Optional[str] = None
    inferred_tool: Optional[str] = None
    confidence: float = 0.0
    line_number: Optional[int] = None
    claim_type: ClaimType = ClaimType.EXPLICIT


class ClaimLog(BaseModel):
    scenario_id: Optional[str] = None
    total_claims: int = 0
    claims: List[Claim] = Field(default_factory=list)
    explicit_claims: List[Claim] = Field(default_factory=list)
    implicit_claims: List[Claim] = Field(default_factory=list)
    vague_statements: List[Claim] = Field(default_factory=list)

