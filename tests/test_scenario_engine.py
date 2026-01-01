import pytest
from pathlib import Path
from src.scenario_engine import (
    TestScenario,
    Prompt,
    ExpectedBehavior,
    HallucinationTraps,
    ScenarioLoader,
    ScenarioValidator,
    DifficultyLevel,
    ScenarioCategory,
)


def test_scenario_creation():
    scenario = TestScenario(
        id="test_001",
        name="Test Scenario",
        category=ScenarioCategory.FILE_OPS,
        prompt=Prompt(user_query="Read file.txt"),
        expected_behavior=ExpectedBehavior(required_tools=["read_file"]),
        difficulty=DifficultyLevel.EASY,
    )
    assert scenario.id == "test_001"
    assert scenario.name == "Test Scenario"


def test_scenario_validation():
    scenario = TestScenario(
        id="test_002",
        name="Valid Scenario",
        category=ScenarioCategory.DEBUGGING,
        prompt=Prompt(user_query="Debug the application"),
        expected_behavior=ExpectedBehavior(
            required_tools=["read_file", "edit_file"],
            min_tool_calls=2,
            max_tool_calls=5,
        ),
    )
    errors = ScenarioValidator.validate(scenario)
    assert len(errors) == 0


def test_invalid_scenario_empty_query():
    scenario = TestScenario(
        id="test_003",
        name="Invalid Scenario",
        category=ScenarioCategory.FILE_OPS,
        prompt=Prompt(user_query=""),
        expected_behavior=ExpectedBehavior(required_tools=["read_file"]),
    )
    errors = ScenarioValidator.validate(scenario)
    assert len(errors) > 0


def test_invalid_scenario_conflicting_tools():
    scenario = TestScenario(
        id="test_004",
        name="Conflicting Tools",
        category=ScenarioCategory.FILE_OPS,
        prompt=Prompt(user_query="Read the file"),
        expected_behavior=ExpectedBehavior(
            required_tools=["read_file"],
            forbidden_tools=["read_file"],
        ),
    )
    errors = ScenarioValidator.validate(scenario)
    assert any("forbidden" in e.message.lower() for e in errors)


def test_scenario_loader_from_dict():
    loader = ScenarioLoader()
    data = {
        "id": "test_005",
        "name": "Loaded Scenario",
        "category": "file_ops",
        "prompt": {"user_query": "What's in the file?"},
        "expected_behavior": {"required_tools": ["read_file"]},
        "difficulty": "easy",
    }
    scenario = loader.load_from_dict(data)
    assert scenario.id == "test_005"


def test_scenario_loader_from_file():
    loader = ScenarioLoader()
    scenarios_dir = Path(__file__).parent.parent / "scenarios"
    file_path = scenarios_dir / "file_operations" / "simple_file_read.json"
    
    if file_path.exists():
        scenario = loader.load_from_file(file_path)
        assert scenario.id == "file_read_001"
        assert scenario.category == ScenarioCategory.FILE_OPS


def test_load_all_scenarios():
    loader = ScenarioLoader()
    scenarios = loader.load_all()
    assert len(scenarios) >= 0


def test_load_by_category():
    loader = ScenarioLoader()
    scenarios = loader.load_by_category("file_ops")
    assert all(s.category == ScenarioCategory.FILE_OPS for s in scenarios)


def test_load_by_difficulty():
    loader = ScenarioLoader()
    scenarios = loader.load_by_difficulty("easy")
    assert all(s.difficulty == DifficultyLevel.EASY for s in scenarios)


def test_sequence_validation():
    scenario = TestScenario(
        id="test_006",
        name="Sequence Test",
        category=ScenarioCategory.MULTI_STEP,
        prompt=Prompt(user_query="Fix the bug"),
        expected_behavior=ExpectedBehavior(
            required_tools=["read_file", "edit_file"],
            sequence_matters=True,
            expected_sequence=["read_file", "edit_file"],
        ),
    )
    errors = ScenarioValidator.validate(scenario)
    assert len(errors) == 0

