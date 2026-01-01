from typing import List, Optional, Any
from .models import (
    ValidationReport,
    ValidationStatus,
    RequirementCheck,
    ConsistencyIssue,
    IssueType,
    IssueSeverity,
)
from src.scenario_engine.models import TestScenario
from src.action_tracker.models import ActionLog, Action
from src.claim_extractor.models import ClaimLog, Claim


class ValidationEngine:
    @staticmethod
    def validate(
        scenario: TestScenario,
        action_log: ActionLog,
        claim_log: ClaimLog,
    ) -> ValidationReport:
        
        required_tools_check = ValidationEngine._check_required_tools(scenario, action_log)
        forbidden_tools_check = ValidationEngine._check_forbidden_tools(scenario, action_log)
        parameters_check = ValidationEngine._check_parameters(scenario, action_log)
        sequence_check = ValidationEngine._check_sequence(scenario, action_log)
        call_count_check = ValidationEngine._check_call_counts(scenario, action_log)
        
        hallucinations = ValidationEngine._detect_hallucinations(claim_log, action_log)
        silent_actions = ValidationEngine._detect_silent_actions(action_log, claim_log)
        mismatches = ValidationEngine._detect_mismatches(claim_log, action_log)
        
        all_issues = hallucinations + silent_actions + mismatches
        
        critical_count = sum(1 for i in all_issues if i.severity == IssueSeverity.CRITICAL)
        high_count = sum(1 for i in all_issues if i.severity == IssueSeverity.HIGH)
        medium_count = sum(1 for i in all_issues if i.severity == IssueSeverity.MEDIUM)
        low_count = sum(1 for i in all_issues if i.severity == IssueSeverity.LOW)
        
        if forbidden_tools_check.status == ValidationStatus.FAIL:
            critical_count += 1
        if required_tools_check.status == ValidationStatus.FAIL:
            high_count += 1
        
        status = ValidationEngine._determine_overall_status(
            critical_count,
            high_count,
            required_tools_check,
            forbidden_tools_check,
        )
        
        return ValidationReport(
            scenario_id=scenario.id,
            pass_fail_status=status,
            required_tools_check=required_tools_check,
            forbidden_tools_check=forbidden_tools_check,
            parameters_check=parameters_check,
            sequence_check=sequence_check,
            call_count_check=call_count_check,
            hallucinations=hallucinations,
            silent_actions=silent_actions,
            mismatches=mismatches,
            total_issues=len(all_issues),
            critical_issues=critical_count,
            high_severity_issues=high_count,
            medium_severity_issues=medium_count,
            low_severity_issues=low_count,
        )

    @staticmethod
    def _check_required_tools(scenario: TestScenario, action_log: ActionLog) -> RequirementCheck:
        required = set(scenario.expected_behavior.required_tools)
        actual = action_log.summary.unique_tools_used
        
        missing = list(required - actual)
        
        if not missing:
            status = ValidationStatus.PASS
        else:
            status = ValidationStatus.FAIL
        
        return RequirementCheck(
            name="Required Tools",
            status=status,
            expected=list(required),
            actual=list(actual),
            missing=missing,
        )

    @staticmethod
    def _check_forbidden_tools(scenario: TestScenario, action_log: ActionLog) -> RequirementCheck:
        forbidden = set(scenario.expected_behavior.forbidden_tools)
        actual = action_log.summary.unique_tools_used
        
        violations = list(forbidden & actual)
        
        if not violations:
            status = ValidationStatus.PASS
        else:
            status = ValidationStatus.FAIL
        
        return RequirementCheck(
            name="Forbidden Tools",
            status=status,
            expected=list(forbidden),
            actual=list(actual),
            extra=violations,
        )

    @staticmethod
    def _check_parameters(scenario: TestScenario, action_log: ActionLog) -> RequirementCheck:
        errors = []
        
        for tool_name, expected_params in scenario.expected_behavior.required_parameters.items():
            actions = [a for a in action_log.actions if a.function_name == tool_name]
            
            if not actions:
                errors.append(f"Tool {tool_name} not called")
                continue
            
            for action in actions:
                for param_name, expected_value in expected_params.items():
                    actual_value = action.arguments.get(param_name)
                    
                    if actual_value is None:
                        errors.append(f"{tool_name}.{param_name}: missing")
                    elif actual_value != expected_value:
                        errors.append(f"{tool_name}.{param_name}: expected {expected_value}, got {actual_value}")
        
        status = ValidationStatus.PASS if not errors else ValidationStatus.FAIL
        
        return RequirementCheck(
            name="Parameters",
            status=status,
            details="; ".join(errors) if errors else None,
        )

    @staticmethod
    def _check_sequence(scenario: TestScenario, action_log: ActionLog) -> Optional[RequirementCheck]:
        if not scenario.expected_behavior.sequence_matters:
            return None
        
        expected = scenario.expected_behavior.expected_sequence
        actual = [a.function_name for a in action_log.actions]
        
        matches = expected == actual[:len(expected)]
        
        status = ValidationStatus.PASS if matches else ValidationStatus.FAIL
        
        return RequirementCheck(
            name="Sequence",
            status=status,
            expected=expected,
            actual=actual,
        )

    @staticmethod
    def _check_call_counts(scenario: TestScenario, action_log: ActionLog) -> Optional[RequirementCheck]:
        min_calls = scenario.expected_behavior.min_tool_calls
        max_calls = scenario.expected_behavior.max_tool_calls
        actual = action_log.total_calls
        
        if min_calls is None and max_calls is None:
            return None
        
        status = ValidationStatus.PASS
        details = None
        
        if min_calls is not None and actual < min_calls:
            status = ValidationStatus.FAIL
            details = f"Too few calls: {actual} < {min_calls}"
        
        if max_calls is not None and actual > max_calls:
            status = ValidationStatus.FAIL
            details = f"Too many calls: {actual} > {max_calls}"
        
        return RequirementCheck(
            name="Call Count",
            status=status,
            expected={"min": min_calls, "max": max_calls},
            actual=actual,
            details=details,
        )

    @staticmethod
    def _detect_hallucinations(claim_log: ClaimLog, action_log: ActionLog) -> List[ConsistencyIssue]:
        issues = []
        
        for claim in claim_log.explicit_claims:
            if not claim.inferred_tool:
                continue
            
            matching_actions = [
                a for a in action_log.actions
                if a.function_name == claim.inferred_tool
            ]
            
            if not matching_actions:
                issues.append(ConsistencyIssue(
                    type=IssueType.CLAIM_WITHOUT_ACTION,
                    severity=IssueSeverity.HIGH,
                    claim=claim.claim_text,
                    expected_tool=claim.inferred_tool,
                    quote=claim.claim_text,
                    explanation=f"LLM claimed to {claim.action_verb} but never called {claim.inferred_tool}",
                ))
        
        return issues

    @staticmethod
    def _detect_silent_actions(action_log: ActionLog, claim_log: ClaimLog) -> List[ConsistencyIssue]:
        issues = []
        
        claimed_tools = {c.inferred_tool for c in claim_log.claims if c.inferred_tool}
        
        for action in action_log.actions:
            if action.function_name not in claimed_tools:
                issues.append(ConsistencyIssue(
                    type=IssueType.ACTION_WITHOUT_CLAIM,
                    severity=IssueSeverity.MEDIUM,
                    action=action.function_name,
                    explanation=f"LLM called {action.function_name} without mentioning it",
                    details={"arguments": action.arguments},
                ))
        
        return issues

    @staticmethod
    def _detect_mismatches(claim_log: ClaimLog, action_log: ActionLog) -> List[ConsistencyIssue]:
        issues = []
        
        return issues

    @staticmethod
    def _determine_overall_status(
        critical_count: int,
        high_count: int,
        required_check: RequirementCheck,
        forbidden_check: RequirementCheck,
    ) -> ValidationStatus:
        
        if critical_count > 0 or forbidden_check.status == ValidationStatus.FAIL:
            return ValidationStatus.FAIL
        
        if high_count > 0 or required_check.status == ValidationStatus.FAIL:
            return ValidationStatus.PARTIAL
        
        return ValidationStatus.PASS

