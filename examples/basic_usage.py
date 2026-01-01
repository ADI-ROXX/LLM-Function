from src.scenario_engine import ScenarioLoader, ScenarioValidator


def main():
    loader = ScenarioLoader()
    
    print("Loading all scenarios...")
    scenarios = loader.load_all()
    print(f"Found {len(scenarios)} scenarios\n")
    
    for scenario in scenarios:
        print(f"ID: {scenario.id}")
        print(f"Name: {scenario.name}")
        print(f"Category: {scenario.category.value}")
        print(f"Difficulty: {scenario.difficulty.value}")
        print(f"Query: {scenario.prompt.user_query}")
        
        errors = ScenarioValidator.validate(scenario)
        if errors:
            print("Validation Errors:")
            for error in errors:
                print(f"  - {error.field}: {error.message}")
        else:
            print("✓ Valid scenario")
        
        print("-" * 80)


if __name__ == "__main__":
    main()

