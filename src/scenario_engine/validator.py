from typing import List, Dict, Any
from .models import TestScenario


class ValidationError:
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message

    def __repr__(self):
        return f"ValidationError(field={self.field}, message={self.message})"


class ScenarioValidator:
    @staticmethod
    def validate(scenario: TestScenario) -> List[ValidationError]:
        errors = []
        
        errors.extend(ScenarioValidator._validate_prompt(scenario))
        errors.extend(ScenarioValidator._validate_expected_behavior(scenario))
        errors.extend(ScenarioValidator._validate_consistency(scenario))
        
        return errors

    @staticmethod
    def _validate_prompt(scenario: TestScenario) -> List[ValidationError]:
        errors = []
        
        if not scenario.prompt.user_query.strip():
            errors.append(ValidationError("prompt.user_query", "Cannot be empty"))
        
        if len(scenario.prompt.user_query) < 10:
            errors.append(ValidationError("prompt.user_query", "Too short (minimum 10 characters)"))
        
        return errors

    @staticmethod
    def _validate_expected_behavior(scenario: TestScenario) -> List[ValidationError]:
        errors = []
        behavior = scenario.expected_behavior
        
        if not behavior.required_tools and not behavior.optional_tools:
            errors.append(ValidationError(
                "expected_behavior",
                "Must specify at least one required or optional tool"
            ))
        
        overlap = set(behavior.required_tools) & set(behavior.forbidden_tools)
        if overlap:
            errors.append(ValidationError(
                "expected_behavior",
                f"Tools cannot be both required and forbidden: {overlap}"
            ))
        
        overlap = set(behavior.optional_tools) & set(behavior.forbidden_tools)
        if overlap:
            errors.append(ValidationError(
                "expected_behavior",
                f"Tools cannot be both optional and forbidden: {overlap}"
            ))
        
        if behavior.sequence_matters:
            if not behavior.expected_sequence:
                errors.append(ValidationError(
                    "expected_behavior.expected_sequence",
                    "Required when sequence_matters is True"
                ))
            else:
                for tool in behavior.expected_sequence:
                    if tool not in behavior.required_tools and tool not in behavior.optional_tools:
                        errors.append(ValidationError(
                            "expected_behavior.expected_sequence",
                            f"Tool '{tool}' in sequence but not in required or optional tools"
                        ))
        
        if behavior.min_tool_calls is not None and behavior.min_tool_calls < 0:
            errors.append(ValidationError(
                "expected_behavior.min_tool_calls",
                "Cannot be negative"
            ))
        
        if behavior.max_tool_calls is not None and behavior.max_tool_calls < 0:
            errors.append(ValidationError(
                "expected_behavior.max_tool_calls",
                "Cannot be negative"
            ))
        
        if (behavior.min_tool_calls is not None and 
            behavior.max_tool_calls is not None and 
            behavior.min_tool_calls > behavior.max_tool_calls):
            errors.append(ValidationError(
                "expected_behavior",
                "min_tool_calls cannot be greater than max_tool_calls"
            ))
        
        for tool_name, params in behavior.required_parameters.items():
            if tool_name not in behavior.required_tools and tool_name not in behavior.optional_tools:
                errors.append(ValidationError(
                    "expected_behavior.required_parameters",
                    f"Tool '{tool_name}' has required parameters but is not in required or optional tools"
                ))
        
        return errors

    @staticmethod
    def _validate_consistency(scenario: TestScenario) -> List[ValidationError]:
        errors = []
        
        if scenario.difficulty.value == "easy" and scenario.expected_time > 30:
            errors.append(ValidationError(
                "expected_time",
                "Easy scenarios should typically complete in under 30 seconds"
            ))
        
        if scenario.difficulty.value == "hard" and scenario.expected_time < 10:
            errors.append(ValidationError(
                "expected_time",
                "Hard scenarios typically take more than 10 seconds"
            ))
        
        return errors

    @staticmethod
    def is_valid(scenario: TestScenario) -> bool:
        return len(ScenarioValidator.validate(scenario)) == 0

