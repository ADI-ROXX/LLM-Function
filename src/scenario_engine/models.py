from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ScenarioCategory(str, Enum):
    FILE_OPS = "file_ops"
    CODE_SEARCH = "code_search"
    DEBUGGING = "debugging"
    MULTI_STEP = "multi_step"
    EDGE_CASES = "edge_cases"
    HALLUCINATION_TESTS = "hallucination_tests"


class Prompt(BaseModel):
    user_query: str
    context: Optional[str] = None
    files_mentioned: List[str] = Field(default_factory=list)


class ExpectedBehavior(BaseModel):
    required_tools: List[str] = Field(default_factory=list)
    optional_tools: List[str] = Field(default_factory=list)
    forbidden_tools: List[str] = Field(default_factory=list)
    required_parameters: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    sequence_matters: bool = False
    expected_sequence: List[str] = Field(default_factory=list)
    min_tool_calls: Optional[int] = None
    max_tool_calls: Optional[int] = None

    @field_validator("expected_sequence")
    @classmethod
    def validate_sequence(cls, v, info):
        if info.data.get("sequence_matters") and not v:
            raise ValueError("expected_sequence required when sequence_matters is True")
        return v


class HallucinationTraps(BaseModel):
    description: str
    common_mistakes: List[str] = Field(default_factory=list)


class TestScenario(BaseModel):
    id: str
    name: str
    category: ScenarioCategory
    prompt: Prompt
    expected_behavior: ExpectedBehavior
    hallucination_traps: Optional[HallucinationTraps] = None
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    expected_time: int = Field(default=10, description="Expected completion time in seconds")

    @field_validator("id")
    @classmethod
    def validate_id(cls, v):
        if not v or not v.strip():
            raise ValueError("id cannot be empty")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("name cannot be empty")
        return v

