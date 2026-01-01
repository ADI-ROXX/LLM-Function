import os
from src.llm_runner import RunnerFactory, LLMConfig, LLMProvider
from src.scenario_engine import ScenarioLoader
from src.tool_system import get_standard_tools


def main():
    print("=== LLM Runner Demo ===\n")
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("Warning: DEEPSEEK_API_KEY not set in environment")
        print("Set it with: export DEEPSEEK_API_KEY=your_key_here\n")
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
        print(f"\nError: {response.error}")
        return
    
    print(f"\n=== Response ===")
    print(f"Model: {response.model}")
    print(f"Latency: {response.metadata.latency_ms:.2f}ms")
    
    if response.metadata.tokens_used:
        print(f"Tokens: {response.metadata.tokens_used}")
    
    if response.metadata.cost:
        print(f"Cost: ${response.metadata.cost:.6f}")
    
    print(f"\n=== Text Response ===")
    print(response.response_text)
    
    print(f"\n=== Function Calls ({len(response.function_calls)}) ===")
    for call in response.function_calls:
        print(f"  {call.sequence_number}. {call.name}({call.arguments})")


def demo_ollama():
    print("\n=== Ollama Runner Demo ===\n")
    
    runner = RunnerFactory.create_ollama_runner(
        model="llama3.2:1b",
        base_url="http://localhost:11434",
    )
    
    loader = ScenarioLoader()
    scenario = loader.load_by_id("file_read_001")
    
    if not scenario:
        print("Scenario not found")
        return
    
    print(f"Running scenario: {scenario.name}")
    print(f"Query: {scenario.prompt.user_query}\n")
    
    tools = get_standard_tools()
    
    print("Calling Ollama...")
    response = runner.run(scenario, tools)
    
    if response.error:
        print(f"\nError: {response.error}")
        return
    
    print(f"\n=== Response ===")
    print(f"Model: {response.model}")
    print(f"Latency: {response.metadata.latency_ms:.2f}ms")
    
    if response.response_text:
        print(f"\n=== Text Response ===")
        print(response.response_text)
    
    print(f"\n=== Function Calls ({len(response.function_calls)}) ===")
    for call in response.function_calls:
        print(f"  {call.sequence_number}. {call.name}({call.arguments})")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "ollama":
        demo_ollama()
    else:
        main()

