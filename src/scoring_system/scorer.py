from typing import Dict
from .models import Score, Subscore, LetterGrade, ScoringCriteria
from src.validation_engine.models import ValidationReport
from src.action_tracker.models import ActionLog
from src.scenario_engine.models import TestScenario


class ScoringSystem:
    CRITERIA = {
        "tool_selection": ScoringCriteria(
            name="Tool Selection Accuracy",
            weight=2.5,
            description="Calls correct tools for the task",
        ),
        "parameters": ScoringCriteria(
            name="Parameter Correctness",
            weight=1.5,
            description="Function parameters are accurate and complete",
        ),
        "sequence": ScoringCriteria(
            name="Execution Sequence",
            weight=1.5,
            description="Tools called in logical, efficient order",
        ),
        "consistency": ScoringCriteria(
            name="Claim-Action Consistency",
            weight=2.5,
            description="Stated intentions match actual actions",
        ),
        "compliance": ScoringCriteria(
            name="Compliance",
            weight=1.0,
            description="Follows constraints (no forbidden tools)",
        ),
        "efficiency": ScoringCriteria(
            name="Efficiency",
            weight=1.0,
            description="Completes task with minimal tool calls",
        ),
    }

    @staticmethod
    def calculate_score(
        validation_report: ValidationReport,
        action_log: ActionLog,
        scenario: TestScenario,
    ) -> Score:
        
        subscores = {}
        
        subscores["tool_selection"] = ScoringSystem._score_tool_selection(
            validation_report, scenario
        )
        
        subscores["parameters"] = ScoringSystem._score_parameters(validation_report)
        
        subscores["sequence"] = ScoringSystem._score_sequence(validation_report, scenario)
        
        subscores["consistency"] = ScoringSystem._score_consistency(validation_report)
        
        subscores["compliance"] = ScoringSystem._score_compliance(validation_report)
        
        subscores["efficiency"] = ScoringSystem._score_efficiency(action_log, scenario)
        
        total = sum(s.weighted_score for s in subscores.values())
        
        grade = ScoringSystem._assign_grade(total)
        
        explanation = ScoringSystem._generate_explanation(subscores, validation_report)
        
        return Score(
            total=round(total, 2),
            subscores=subscores,
            grade=grade,
            percentile=round(total * 10, 2),
            explanation=explanation,
        )

    @staticmethod
    def _score_tool_selection(validation_report: ValidationReport, scenario: TestScenario) -> Subscore:
        criterion = ScoringSystem.CRITERIA["tool_selection"]
        
        score = 10.0
        explanation = []
        
        missing = len(validation_report.required_tools_check.missing)
        if missing > 0:
            penalty = missing * 3
            score -= penalty
            explanation.append(f"Missing {missing} required tool(s)")
        
        violations = len(validation_report.forbidden_tools_check.extra)
        if violations > 0:
            score = 0
            explanation.append(f"Used {violations} forbidden tool(s)")
        
        score = max(0, score)
        weighted = (score / 10.0) * criterion.weight
        
        return Subscore(
            criterion=criterion.name,
            score=score,
            weight=criterion.weight,
            weighted_score=weighted,
            explanation="; ".join(explanation) if explanation else "All required tools called correctly",
        )

    @staticmethod
    def _score_parameters(validation_report: ValidationReport) -> Subscore:
        criterion = ScoringSystem.CRITERIA["parameters"]
        
        score = 10.0
        explanation = "All parameters correct"
        
        if validation_report.parameters_check.status.value != "pass":
            errors = validation_report.parameters_check.details
            if errors:
                error_count = len(errors.split(";"))
                penalty = error_count * 3
                score = max(0, 10 - penalty)
                explanation = f"{error_count} parameter error(s)"
        
        weighted = (score / 10.0) * criterion.weight
        
        return Subscore(
            criterion=criterion.name,
            score=score,
            weight=criterion.weight,
            weighted_score=weighted,
            explanation=explanation,
        )

    @staticmethod
    def _score_sequence(validation_report: ValidationReport, scenario: TestScenario) -> Subscore:
        criterion = ScoringSystem.CRITERIA["sequence"]
        
        score = 10.0
        explanation = "Correct sequence"
        
        if scenario.expected_behavior.sequence_matters:
            if validation_report.sequence_check and validation_report.sequence_check.status.value != "pass":
                score = 5.0
                explanation = "Incorrect sequence"
        
        weighted = (score / 10.0) * criterion.weight
        
        return Subscore(
            criterion=criterion.name,
            score=score,
            weight=criterion.weight,
            weighted_score=weighted,
            explanation=explanation,
        )

    @staticmethod
    def _score_consistency(validation_report: ValidationReport) -> Subscore:
        criterion = ScoringSystem.CRITERIA["consistency"]
        
        score = 10.0
        
        hallucinations = len(validation_report.hallucinations)
        silent_actions = len(validation_report.silent_actions)
        
        score -= (hallucinations * 4)
        score -= (silent_actions * 2)
        
        score = max(0, score)
        
        explanation_parts = []
        if hallucinations > 0:
            explanation_parts.append(f"{hallucinations} hallucination(s)")
        if silent_actions > 0:
            explanation_parts.append(f"{silent_actions} silent action(s)")
        
        explanation = "; ".join(explanation_parts) if explanation_parts else "Perfect consistency"
        
        weighted = (score / 10.0) * criterion.weight
        
        return Subscore(
            criterion=criterion.name,
            score=score,
            weight=criterion.weight,
            weighted_score=weighted,
            explanation=explanation,
        )

    @staticmethod
    def _score_compliance(validation_report: ValidationReport) -> Subscore:
        criterion = ScoringSystem.CRITERIA["compliance"]
        
        violations = len(validation_report.forbidden_tools_check.extra)
        
        score = 0 if violations > 0 else 10.0
        explanation = "Full compliance" if score == 10 else f"Used {violations} forbidden tool(s)"
        
        weighted = (score / 10.0) * criterion.weight
        
        return Subscore(
            criterion=criterion.name,
            score=score,
            weight=criterion.weight,
            weighted_score=weighted,
            explanation=explanation,
        )

    @staticmethod
    def _score_efficiency(action_log: ActionLog, scenario: TestScenario) -> Subscore:
        criterion = ScoringSystem.CRITERIA["efficiency"]
        
        actual = action_log.total_calls
        expected = len(scenario.expected_behavior.required_tools)
        
        if expected == 0:
            expected = 1
        
        ratio = actual / expected
        
        if ratio <= 1.0:
            score = 10.0
            explanation = "Optimal efficiency"
        elif ratio <= 1.5:
            score = 7.0
            explanation = "Minor inefficiency"
        else:
            score = max(0, 10 - ((ratio - 1) * 10))
            explanation = f"Inefficient ({ratio:.1f}x expected calls)"
        
        weighted = (score / 10.0) * criterion.weight
        
        return Subscore(
            criterion=criterion.name,
            score=score,
            weight=criterion.weight,
            weighted_score=weighted,
            explanation=explanation,
        )

    @staticmethod
    def _assign_grade(total: float) -> LetterGrade:
        if total >= 9.0:
            return LetterGrade.A_PLUS
        elif total >= 8.0:
            return LetterGrade.A
        elif total >= 7.0:
            return LetterGrade.B
        elif total >= 6.0:
            return LetterGrade.C
        elif total >= 5.0:
            return LetterGrade.D
        else:
            return LetterGrade.F

    @staticmethod
    def _generate_explanation(subscores: Dict[str, Subscore], validation_report: ValidationReport) -> str:
        parts = []
        
        for name, subscore in subscores.items():
            if subscore.score < 7.0:
                parts.append(f"{subscore.criterion}: {subscore.explanation}")
        
        if not parts:
            return "Excellent performance across all criteria"
        
        return "; ".join(parts)

