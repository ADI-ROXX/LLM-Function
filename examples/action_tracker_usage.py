import os
from src.llm_runner import RunnerFactory, LLMProvider, LLMConfig
from src.scenario_engine import ScenarioLoader
from src.tool_system import get_standard_tools
from src.action_tracker import ActionTracker


def main():
    print("=== Action Tracker Demo ===\n")
    
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
    
    scenario = loader.load_by_id("file_read_001")
    if not scenario:
        print("Scenario not found")
        return
    
    print(f"Running scenario: {scenario.name}")
    print(f"Query: {scenario.prompt.user_query}\n")
    
    tools = get_standard_tools()
    
    print("Calling LLM...")
    response = runner.run(scenario, tools)
    
    if response.error:
        print(f"Error: {response.error}")
        return
    
    print(f"Response: {response.response_text}\n")
    
    print("=== Extracting Actions ===\n")
    action_log = ActionTracker.extract_actions(response)
    
    print(f"Total calls: {action_log.total_calls}")
    print(f"Unique tools used: {action_log.summary.unique_tools_used}")
    print(f"Tools called multiple times: {action_log.summary.tools_called_multiple_times}")
    print(f"Execution time: {action_log.summary.total_execution_time_ms:.2f}ms\n")
    
    print("=== Actions ===")
    for action in action_log.actions:
        print(f"  {action.sequence_number}. {action.function_name}")
        print(f"     Arguments: {action.arguments}")
        
        errors = ActionTracker.validate_arguments_structure(action)
        if errors:
            print(f"     Validation errors: {errors}")
        else:
            print(f"     ✓ Valid arguments")
        print()
    
    print("=== Tool Analysis ===")
    for tool_name, count in action_log.summary.tool_call_counts.items():
        print(f"  {tool_name}: called {count} time(s)")
    
    print(f"\n=== Sequence ===")
    sequence = ActionTracker.get_tools_in_sequence(action_log)
    print(f"  {' -> '.join(sequence)}")


if __name__ == "__main__":
    main()

