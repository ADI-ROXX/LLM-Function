import json
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from src.scenario_engine.models import TestScenario
from src.validation_engine.models import ValidationReport
from src.scoring_system.models import Score
from src.action_tracker.models import ActionLog
from src.claim_extractor.models import ClaimLog
from src.llm_runner.models import LLMResponse


class ReportGenerator:
    def __init__(self):
        self.console = Console()

    def generate_text_report(
        self,
        scenario: TestScenario,
        response: LLMResponse,
        action_log: ActionLog,
        claim_log: ClaimLog,
        validation_report: ValidationReport,
        score: Score,
    ) -> str:
        
        lines = []
        lines.append("=" * 80)
        lines.append("EVALUATION REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        lines.append("METADATA")
        lines.append("-" * 80)
        lines.append(f"Scenario ID: {scenario.id}")
        lines.append(f"Scenario Name: {scenario.name}")
        lines.append(f"LLM Model: {response.model}")
        lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        lines.append(f"OVERALL SCORE: {score.total}/10 (Grade: {score.grade.value})")
        lines.append(f"Status: {validation_report.pass_fail_status.value.upper()}")
        lines.append("")
        lines.append("=" * 80)
        lines.append("")
        
        lines.append("SCENARIO DETAILS")
        lines.append("-" * 80)
        lines.append(f"Prompt: {scenario.prompt.user_query}")
        lines.append("")
        lines.append("Expected Behavior:")
        lines.append(f"  Required tools: {', '.join(scenario.expected_behavior.required_tools)}")
        if scenario.expected_behavior.forbidden_tools:
            lines.append(f"  Forbidden tools: {', '.join(scenario.expected_behavior.forbidden_tools)}")
        lines.append(f"  Difficulty: {scenario.difficulty.value}")
        lines.append("")
        lines.append("=" * 80)
        lines.append("")
        
        lines.append("SUBSCORES")
        lines.append("-" * 80)
        for name, subscore in score.subscores.items():
            bar = self._create_bar(subscore.score, 10)
            lines.append(f"{subscore.criterion:.<30} {subscore.score:>4.1f}/10 {bar} (Weight: {subscore.weight})")
        lines.append("")
        lines.append("=" * 80)
        lines.append("")
        
        lines.append("DETAILED FINDINGS")
        lines.append("-" * 80)
        lines.append("")
        
        passed_checks = []
        if validation_report.required_tools_check.status.value == "pass":
            passed_checks.append("Required tools called")
        if validation_report.forbidden_tools_check.status.value == "pass":
            passed_checks.append("No forbidden tools used")
        if validation_report.parameters_check.status.value == "pass":
            passed_checks.append("Parameters correct")
        
        if passed_checks:
            lines.append(f"✅ PASSED CHECKS ({len(passed_checks)})")
            for i, check in enumerate(passed_checks, 1):
                lines.append(f"  {i}. {check}")
            lines.append("")
        
        warnings = validation_report.silent_actions
        if warnings:
            lines.append(f"⚠️  WARNINGS ({len(warnings)})")
            for i, warning in enumerate(warnings, 1):
                lines.append(f"  {i}. {warning.type.value.upper()}")
                lines.append(f"     {warning.explanation}")
            lines.append("")
        
        failures = validation_report.hallucinations + [
            issue for issue in []
            if validation_report.required_tools_check.status.value == "fail"
        ]
        
        if validation_report.required_tools_check.status.value == "fail":
            lines.append(f"❌ FAILED CHECKS")
            for tool in validation_report.required_tools_check.missing:
                lines.append(f"  - Missing required tool: {tool}")
            lines.append("")
        
        if validation_report.hallucinations:
            lines.append(f"❌ HALLUCINATIONS ({len(validation_report.hallucinations)})")
            for i, hall in enumerate(validation_report.hallucinations, 1):
                lines.append(f"  {i}. {hall.explanation}")
                lines.append(f"     Quote: \"{hall.quote}\"")
            lines.append("")
        
        lines.append("=" * 80)
        lines.append("")
        
        lines.append("LLM RESPONSE ANALYSIS")
        lines.append("-" * 80)
        lines.append("")
        lines.append("What the LLM Said:")
        lines.append(f"  {response.response_text or 'No text response'}")
        lines.append("")
        lines.append(f"Extracted Claims ({claim_log.total_claims}):")
        for claim in claim_log.claims[:5]:
            lines.append(f"  - \"{claim.claim_text}\" → {claim.inferred_tool} (confidence: {claim.confidence:.2f})")
        lines.append("")
        lines.append(f"What the LLM Did ({action_log.total_calls} calls):")
        for action in action_log.actions:
            args_str = ", ".join(f"{k}={v}" for k, v in action.arguments.items())
            lines.append(f"  {action.sequence_number}. {action.function_name}({args_str})")
        lines.append("")
        lines.append("=" * 80)
        lines.append("")
        
        lines.append("PERFORMANCE METRICS")
        lines.append("-" * 80)
        lines.append(f"Total Tool Calls: {action_log.total_calls}")
        lines.append(f"Expected Minimum: {scenario.expected_behavior.min_tool_calls or 'N/A'}")
        lines.append(f"Expected Maximum: {scenario.expected_behavior.max_tool_calls or 'N/A'}")
        lines.append("")
        lines.append(f"Response Latency: {response.metadata.latency_ms:.0f}ms")
        if response.metadata.tokens_used:
            lines.append(f"Tokens Used: {response.metadata.tokens_used}")
        if response.metadata.cost:
            lines.append(f"Estimated Cost: ${response.metadata.cost:.6f}")
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)

    def print_report(
        self,
        scenario: TestScenario,
        response: LLMResponse,
        action_log: ActionLog,
        claim_log: ClaimLog,
        validation_report: ValidationReport,
        score: Score,
    ) -> None:
        
        self.console.print("\n")
        self.console.print(Panel.fit(
            f"[bold]EVALUATION REPORT[/bold]\n"
            f"Score: [bold]{score.total}/10[/bold] ({score.grade.value}) | "
            f"Status: [bold]{validation_report.pass_fail_status.value.upper()}[/bold]",
            border_style="cyan"
        ))
        
        self.console.print(f"\n[bold]Scenario:[/bold] {scenario.name}")
        self.console.print(f"[bold]Query:[/bold] {scenario.prompt.user_query}")
        self.console.print(f"[bold]Model:[/bold] {response.model}\n")
        
        table = Table(title="Subscores")
        table.add_column("Criterion", style="cyan")
        table.add_column("Score", justify="right")
        table.add_column("Progress", justify="center")
        
        for subscore in score.subscores.values():
            bar = self._create_rich_bar(subscore.score, 10)
            table.add_row(
                subscore.criterion,
                f"{subscore.score:.1f}/10",
                bar
            )
        
        self.console.print(table)
        
        self.console.print(f"\n[bold green]✓ Passed:[/bold green] {self._count_passed(validation_report)}")
        self.console.print(f"[bold yellow]⚠ Warnings:[/bold yellow] {validation_report.medium_severity_issues}")
        self.console.print(f"[bold red]✗ Failed:[/bold red] {validation_report.high_severity_issues + validation_report.critical_issues}")
        
        self.console.print("")

    def export_json(
        self,
        scenario: TestScenario,
        response: LLMResponse,
        action_log: ActionLog,
        claim_log: ClaimLog,
        validation_report: ValidationReport,
        score: Score,
        output_file: str,
    ) -> None:
        
        data = {
            "metadata": {
                "scenario_id": scenario.id,
                "scenario_name": scenario.name,
                "model": response.model,
                "timestamp": datetime.now().isoformat(),
            },
            "score": score.model_dump(),
            "validation": {
                "status": validation_report.pass_fail_status.value,
                "total_issues": validation_report.total_issues,
                "critical_issues": validation_report.critical_issues,
                "high_issues": validation_report.high_severity_issues,
                "medium_issues": validation_report.medium_severity_issues,
            },
            "actions": {
                "total_calls": action_log.total_calls,
                "tools_used": list(action_log.summary.unique_tools_used),
                "actions": [a.model_dump() for a in action_log.actions],
            },
            "claims": {
                "total_claims": claim_log.total_claims,
                "claims": [c.model_dump() for c in claim_log.claims],
            },
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def _create_bar(self, value: float, max_value: float, length: int = 10) -> str:
        filled = int((value / max_value) * length)
        return "█" * filled + "░" * (length - filled)

    def _create_rich_bar(self, value: float, max_value: float, length: int = 20) -> str:
        filled = int((value / max_value) * length)
        bar = "█" * filled + "░" * (length - filled)
        
        if value >= 8:
            color = "green"
        elif value >= 6:
            color = "yellow"
        else:
            color = "red"
        
        return f"[{color}]{bar}[/{color}]"

    def _count_passed(self, validation_report: ValidationReport) -> int:
        count = 0
        if validation_report.required_tools_check.status.value == "pass":
            count += 1
        if validation_report.forbidden_tools_check.status.value == "pass":
            count += 1
        if validation_report.parameters_check.status.value == "pass":
            count += 1
        return count

