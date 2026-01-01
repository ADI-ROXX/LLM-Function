from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class Action(BaseModel):
    sequence_number: int
    function_name: str
    arguments: Dict[str, Any]
    timestamp: Optional[datetime] = None
    raw_call_object: Optional[Dict[str, Any]] = None
    call_id: Optional[str] = None


class ActionSummary(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    unique_tools_used: set = Field(default_factory=set)
    tools_called_multiple_times: List[str] = Field(default_factory=list)
    tool_call_counts: Dict[str, int] = Field(default_factory=dict)
    total_execution_time_ms: Optional[float] = None


class ActionLog(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    scenario_id: Optional[str] = None
    total_calls: int = 0
    actions: List[Action] = Field(default_factory=list)
    summary: ActionSummary = Field(default_factory=ActionSummary)

