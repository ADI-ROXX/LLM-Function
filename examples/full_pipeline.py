import os
from src.llm_runner import RunnerFactory, LLMConfig, LLMProvider
from src.scenario_engine import ScenarioLoader
from src.tool_system import get_standard_tools
from src.action_tracker import ActionTracker
from src.claim_extractor import ClaimExtractor
from src.validation_engine import ValidationEngine
from src.scoring_system import ScoringSystem
from src.report_generator import ReportGenerator


def main():
    print("=== Full Pipeline Demo ===\n")
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("Warning: DEEPSEEK_API_KEY not set")
        return
    
    config = LLMConfig(
        provider=LLMProvider.DEEPSEEK,
        model="deepseek-chat",
        api_key=api_key,
        temperature=0.7,
    )
    
    runner = RunnerFactory.create_runner(config)
    loader = ScenarioLoader()
    generator = ReportGenerator()
    
    scenario = loader.load_by_id("file_read_001")
    if not scenario:
        print("Scenario not found")
        return
    
    print(f"Testing scenario: {scenario.name}\n")
    
    tools = get_standard_tools()
    
    print("Step 1: Running LLM...")
    response = runner.run(scenario, tools)
    
    if response.error:
        print(f"Error: {response.error}")
        return
    
    print("Step 2: Extracting actions...")
    action_log = ActionTracker.extract_actions(response)
    
    print("Step 3: Extracting claims...")
    claim_log = ClaimExtractor.extract_claims(response)
    
    print("Step 4: Validating...")
    validation_report = ValidationEngine.validate(scenario, action_log, claim_log)
    
    print("Step 5: Scoring...")
    score = ScoringSystem.calculate_score(validation_report, action_log, scenario)
    
    print("Step 6: Generating report...\n")
    
    generator.print_report(
        scenario,
        response,
        action_log,
        claim_log,
        validation_report,
        score,
    )
    
    text_report = generator.generate_text_report(
        scenario,
        response,
        action_log,
        claim_log,
        validation_report,
        score,
    )
    
    with open("evaluation_report.txt", "w") as f:
        f.write(text_report)
    
    print("\n✓ Text report saved to evaluation_report.txt")
    
    generator.export_json(
        scenario,
        response,
        action_log,
        claim_log,
        validation_report,
        score,
        "evaluation_report.json",
    )
    
    print("✓ JSON report saved to evaluation_report.json")


if __name__ == "__main__":
    main()

