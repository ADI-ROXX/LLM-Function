from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class LLMProvider(str, Enum):
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"


class LLMConfig(BaseModel):
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 60


class FunctionCall(BaseModel):
    id: Optional[str] = None
    name: str
    arguments: Dict[str, Any]
    sequence_number: int


class ResponseMetadata(BaseModel):
    latency_ms: float
    tokens_used: Optional[int] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    cost: Optional[float] = None
    model: str
    timestamp: datetime = Field(default_factory=datetime.now)


class LLMResponse(BaseModel):
    scenario_id: Optional[str] = None
    provider: LLMProvider
    model: str
    response_text: Optional[str] = None
    function_calls: List[FunctionCall] = Field(default_factory=list)
    metadata: ResponseMetadata
    raw_response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

