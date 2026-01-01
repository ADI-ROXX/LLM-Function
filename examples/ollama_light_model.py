"""
Example: Using Ollama with a Light LLM (~5GB)

This script demonstrates how to use Ollama with lightweight models
for function calling evaluation. Perfect for local testing without API keys.

Recommended models:
- llama3.2:3b (2.0GB) - Fast, good function calling
- mistral:7b (4.1GB) - Excellent performance
- gemma:7b (4.8GB) - Google's model
- llama3.1:8b (4.7GB) - Great balance
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
import requests
from src.llm_runner import RunnerFactory, LLMConfig, LLMProvider
from src.scenario_engine import ScenarioLoader
from src.tool_system import get_standard_tools
from src.action_tracker import ActionTracker
from src.claim_extractor import ClaimExtractor
from src.validation_engine import ValidationEngine
from src.scoring_system import ScoringSystem
from src.report_generator import ReportGenerator


def check_ollama_connection(base_url: str) -> bool:
    """Check if Ollama is running and accessible"""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def get_available_models(base_url: str) -> list:
    """Get list of available models from Ollama"""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
    except Exception:
        pass
    return []


def main():
    print("=== Ollama Light Model Demo ===\n")
    
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Check if Ollama is running
    if not check_ollama_connection(base_url):
        print("❌ Error: Cannot connect to Ollama!")
        print(f"\nMake sure Ollama is running:")
        print(f"  1. Start Ollama: ollama serve")
        print(f"  2. Verify it's running: curl {base_url}/api/tags")
        return
    
    # Get available models
    available_models = get_available_models(base_url)
    
    if not available_models:
        print("❌ Error: No models found in Ollama!")
        print(f"\nInstall a model first:")
        print(f"  ollama pull mistral:7b    # Recommended (4.1GB)")
        print(f"  ollama pull llama3.2:3b   # Fast (2.0GB)")
        return
    
    print(f"Available models: {', '.join(available_models)}\n")
    
    # Choose your model (adjust based on what you have installed)
    # Available light models (~5GB):
    # - llama3.2:3b (2.0GB) - Fastest
    # - mistral:7b (4.1GB) - Recommended
    # - gemma:7b (4.8GB)
    # - llama3.1:8b (4.7GB)
    
    model_name = os.getenv("OLLAMA_MODEL")
    
    # If no model specified, try to use an available one
    if not model_name:
        # Prefer mistral:7b, then gemma, then any available
        if "mistral:7b" in available_models:
            model_name = "mistral:7b"
        elif "gemma3:4b" in available_models or "gemma:7b" in available_models:
            model_name = "gemma3:4b" if "gemma3:4b" in available_models else "gemma:7b"
        else:
            model_name = available_models[0]
    
    # Verify the model is available
    if model_name not in available_models:
        print(f"❌ Error: Model '{model_name}' not found!")
        print(f"\nAvailable models: {', '.join(available_models)}")
        print(f"\nTo install the model:")
        print(f"  ollama pull {model_name}")
        return
    
    print(f"Using model: {model_name}")
    print(f"Ollama URL: {base_url}\n")
    
    # Create Ollama runner
    config = LLMConfig(
        provider=LLMProvider.OLLAMA,
        model=model_name,
        base_url=base_url,
        temperature=0.7,
        timeout=120,  # Longer timeout for local models
    )
    
    runner = RunnerFactory.create_runner(config)
    loader = ScenarioLoader()
    generator = ReportGenerator()
    
    # Load a test scenario
    scenario = loader.load_by_id("file_read_001")
    if not scenario:
        print("Scenario not found. Available scenarios:")
        all_scenarios = loader.load_all()
        for s in all_scenarios[:5]:  # Show first 5
            print(f"  - {s.id}: {s.name}")
        return
    
    print(f"Testing scenario: {scenario.name}")
    print(f"Query: {scenario.prompt.user_query}\n")
    
    tools = get_standard_tools()
    
    print("Step 1: Running LLM with Ollama...")
    try:
        response = runner.run(scenario, tools)
    except requests.exceptions.HTTPError as e:
        if e.response and e.response.status_code == 404:
            print(f"❌ Error: Model '{model_name}' not found or endpoint not available")
            print(f"\nAvailable models: {', '.join(available_models)}")
            print(f"\nTo install the model:")
            print(f"  ollama pull {model_name}")
        else:
            print(f"❌ HTTP Error: {e}")
        return
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Cannot connect to Ollama at {base_url}")
        print("\nMake sure Ollama is running:")
        print("  1. Start Ollama: ollama serve")
        print("  2. Verify: curl http://localhost:11434/api/tags")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"\nTroubleshooting:")
        print(f"  1. Check Ollama is running: ollama serve")
        print(f"  2. Verify model is installed: ollama list")
        print(f"  3. Test model directly: ollama run {model_name}")
        return
    
    if response.error:
        print(f"Error: {response.error}")
        return
    
    print(f"✓ Response received (latency: {response.metadata.latency_ms:.0f}ms)")
    
    print("\nStep 2: Extracting actions...")
    action_log = ActionTracker.extract_actions(response)
    print(f"✓ Found {action_log.total_calls} function calls")
    
    print("\nStep 3: Extracting claims...")
    claim_log = ClaimExtractor.extract_claims(response)
    print(f"✓ Found {claim_log.total_claims} claims")
    
    print("\nStep 4: Validating...")
    validation_report = ValidationEngine.validate(scenario, action_log, claim_log)
    print(f"✓ Validation complete ({validation_report.pass_fail_status.value})")
    
    print("\nStep 5: Scoring...")
    score = ScoringSystem.calculate_score(validation_report, action_log, scenario)
    print(f"✓ Score: {score.total:.1f}/10 ({score.grade.value})")
    
    print("\nStep 6: Generating report...\n")
    
    # Print console report
    generator.print_report(
        scenario,
        response,
        action_log,
        claim_log,
        validation_report,
        score,
    )
    
    # Save text report
    text_report = generator.generate_text_report(
        scenario,
        response,
        action_log,
        claim_log,
        validation_report,
        score,
    )
    
    report_file = f"ollama_evaluation_{model_name.replace(':', '_')}.txt"
    with open(report_file, "w") as f:
        f.write(text_report)
    
    print(f"\n✓ Text report saved to {report_file}")
    
    # Save JSON report
    json_file = f"ollama_evaluation_{model_name.replace(':', '_')}.json"
    generator.export_json(
        scenario,
        response,
        action_log,
        claim_log,
        validation_report,
        score,
        json_file,
    )
    
    print(f"✓ JSON report saved to {json_file}")


def test_multiple_models():
    """Test multiple light models and compare results"""
    print("=== Testing Multiple Light Models ===\n")
    
    models = [
        "llama3.2:3b",
        "mistral:7b",
        "gemma:7b",
    ]
    
    loader = ScenarioLoader()
    scenario = loader.load_by_id("file_read_001")
    tools = get_standard_tools()
    
    results = []
    
    for model_name in models:
        print(f"\n{'='*50}")
        print(f"Testing: {model_name}")
        print(f"{'='*50}\n")
        
        try:
            config = LLMConfig(
                provider=LLMProvider.OLLAMA,
                model=model_name,
                base_url="http://localhost:11434",
                temperature=0.7,
                timeout=120,
            )
            
            runner = RunnerFactory.create_runner(config)
            response = runner.run(scenario, tools)
            
            if response.error:
                print(f"✗ Error: {response.error}")
                continue
            
            action_log = ActionTracker.extract_actions(response)
            claim_log = ClaimExtractor.extract_claims(response)
            validation_report = ValidationEngine.validate(scenario, action_log, claim_log)
            score = ScoringSystem.calculate_score(validation_report, action_log, scenario)
            
            results.append({
                "model": model_name,
                "score": score.total,
                "grade": score.grade.value,
                "latency": response.metadata.latency_ms,
                "function_calls": action_log.total_calls,
            })
            
            print(f"✓ Score: {score.total:.1f}/10 ({score.grade.value})")
            print(f"✓ Latency: {response.metadata.latency_ms:.0f}ms")
            print(f"✓ Function calls: {action_log.total_calls}")
            
        except Exception as e:
            print(f"✗ Failed: {e}")
            continue
    
    # Print comparison
    if results:
        print(f"\n{'='*50}")
        print("Comparison Summary")
        print(f"{'='*50}\n")
        print(f"{'Model':<20} {'Score':<10} {'Grade':<8} {'Latency':<12} {'Calls':<8}")
        print("-" * 60)
        for r in results:
            print(f"{r['model']:<20} {r['score']:<10.1f} {r['grade']:<8} {r['latency']:<12.0f}ms {r['function_calls']:<8}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "compare":
        test_multiple_models()
    else:
        main()

