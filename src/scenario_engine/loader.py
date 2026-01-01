import json
import yaml
from pathlib import Path
from typing import List, Optional, Union
from .models import TestScenario


class ScenarioLoader:
    def __init__(self, scenarios_dir: Optional[Union[str, Path]] = None):
        if scenarios_dir is None:
            self.scenarios_dir = Path(__file__).parent.parent.parent / "scenarios"
        else:
            self.scenarios_dir = Path(scenarios_dir)
        
        self.scenarios_dir.mkdir(parents=True, exist_ok=True)

    def load_from_file(self, file_path: Union[str, Path]) -> TestScenario:
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Scenario file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            if file_path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif file_path.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        return TestScenario(**data)

    def load_from_dict(self, data: dict) -> TestScenario:
        return TestScenario(**data)

    def load_all(self) -> List[TestScenario]:
        scenarios = []
        
        for file_path in self.scenarios_dir.rglob("*.json"):
            try:
                scenario = self.load_from_file(file_path)
                scenarios.append(scenario)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        for file_path in self.scenarios_dir.rglob("*.yaml"):
            try:
                scenario = self.load_from_file(file_path)
                scenarios.append(scenario)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        for file_path in self.scenarios_dir.rglob("*.yml"):
            try:
                scenario = self.load_from_file(file_path)
                scenarios.append(scenario)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return scenarios

    def load_by_category(self, category: str) -> List[TestScenario]:
        all_scenarios = self.load_all()
        return [s for s in all_scenarios if s.category.value == category]

    def load_by_difficulty(self, difficulty: str) -> List[TestScenario]:
        all_scenarios = self.load_all()
        return [s for s in all_scenarios if s.difficulty.value == difficulty]

    def load_by_id(self, scenario_id: str) -> Optional[TestScenario]:
        all_scenarios = self.load_all()
        for scenario in all_scenarios:
            if scenario.id == scenario_id:
                return scenario
        return None

    def save_to_file(self, scenario: TestScenario, file_path: Union[str, Path]) -> None:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            if file_path.suffix in ['.yaml', '.yml']:
                yaml.dump(scenario.model_dump(), f, default_flow_style=False)
            elif file_path.suffix == '.json':
                json.dump(scenario.model_dump(), f, indent=2)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")

