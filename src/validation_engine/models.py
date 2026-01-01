from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class ValidationStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    PARTIAL = "partial"


class IssueSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueType(str, Enum):
    MISSING_REQUIRED_TOOL = "missing_required_tool"
    FORBIDDEN_TOOL_USED = "forbidden_tool_used"
    WRONG_PARAMETER = "wrong_parameter"
    WRONG_SEQUENCE = "wrong_sequence"
    CLAIM_WITHOUT_ACTION = "claim_without_action"
    ACTION_WITHOUT_CLAIM = "action_without_claim"
    CLAIM_ACTION_MISMATCH = "claim_action_mismatch"
    TOO_FEW_CALLS = "too_few_calls"
    TOO_MANY_CALLS = "too_many_calls"


class RequirementCheck(BaseModel):
    name: str
    status: ValidationStatus
    expected: Optional[Any] = None
    actual: Optional[Any] = None
    missing: List[str] = Field(default_factory=list)
    extra: List[str] = Field(default_factory=list)
    details: Optional[str] = None


class ConsistencyIssue(BaseModel):
    type: IssueType
    severity: IssueSeverity
    claim: Optional[str] = None
    action: Optional[str] = None
    expected_tool: Optional[str] = None
    actual_tool: Optional[str] = None
    quote: Optional[str] = None
    explanation: str
    details: Optional[Dict[str, Any]] = None


class ValidationReport(BaseModel):
    scenario_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    pass_fail_status: ValidationStatus
    
    required_tools_check: RequirementCheck
    forbidden_tools_check: RequirementCheck
    parameters_check: RequirementCheck
    sequence_check: Optional[RequirementCheck] = None
    call_count_check: Optional[RequirementCheck] = None
    
    hallucinations: List[ConsistencyIssue] = Field(default_factory=list)
    silent_actions: List[ConsistencyIssue] = Field(default_factory=list)
    mismatches: List[ConsistencyIssue] = Field(default_factory=list)
    
    total_issues: int = 0
    critical_issues: int = 0
    high_severity_issues: int = 0
    medium_severity_issues: int = 0
    low_severity_issues: int = 0

