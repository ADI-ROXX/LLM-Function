from typing import Dict
from enum import Enum
from pydantic import BaseModel, Field


class LetterGrade(str, Enum):
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class ScoringCriteria(BaseModel):
    name: str
    weight: float
    description: str


class Subscore(BaseModel):
    criterion: str
    score: float
    max_score: float = 10.0
    weight: float
    weighted_score: float
    explanation: str


class Score(BaseModel):
    total: float
    max_total: float = 10.0
    subscores: Dict[str, Subscore] = Field(default_factory=dict)
    grade: LetterGrade
    percentile: float
    explanation: str

