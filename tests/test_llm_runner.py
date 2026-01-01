import pytest
from unittest.mock import Mock, patch
from src.llm_runner import (
    LLMConfig,
    LLMProvider,
    RunnerFactory,
    DeepseekRunner,
    OllamaRunner,
)
from src.scenario_engine.models import TestScenario, Prompt, ExpectedBehavior, ScenarioCategory
from src.tool_system import get_standard_tools


def test_config_creation():
    config = LLMConfig(
        provider=LLMProvider.DEEPSEEK,
        model="deepseek-chat",
        api_key="test-key",
        temperature=0.7,
    )
    assert config.provider == LLMProvider.DEEPSEEK
    assert config.model == "deepseek-chat"


def test_runner_factory_deepseek():
    config = LLMConfig(
        provider=LLMProvider.DEEPSEEK,
        model="deepseek-chat",
        api_key="test-key",
    )
    runner = RunnerFactory.create_runner(config)
    assert isinstance(runner, DeepseekRunner)


def test_runner_factory_ollama():
    config = LLMConfig(
        provider=LLMProvider.OLLAMA,
        model="llama3.2:1b",
    )
    runner = RunnerFactory.create_runner(config)
    assert isinstance(runner, OllamaRunner)


def test_runner_factory_create_deepseek():
    runner = RunnerFactory.create_deepseek_runner(
        model="deepseek-chat",
        api_key="test-key",
    )
    assert isinstance(runner, DeepseekRunner)


def test_runner_factory_create_ollama():
    runner = RunnerFactory.create_ollama_runner(
        model="llama3.2:1b",
    )
    assert isinstance(runner, OllamaRunner)


def test_build_messages():
    config = LLMConfig(
        provider=LLMProvider.DEEPSEEK,
        model="deepseek-chat",
        api_key="test-key",
    )
    runner = DeepseekRunner(config)
    
    scenario = TestScenario(
        id="test_001",
        name="Test",
        category=ScenarioCategory.FILE_OPS,
        prompt=Prompt(
            user_query="Read file.txt",
            context="This is a test",
        ),
        expected_behavior=ExpectedBehavior(required_tools=["read_file"]),
    )
    
    messages = runner._build_messages(scenario)
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "This is a test"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Read file.txt"


def test_build_messages_with_system_prompt():
    config = LLMConfig(
        provider=LLMProvider.DEEPSEEK,
        model="deepseek-chat",
        api_key="test-key",
    )
    runner = DeepseekRunner(config)
    
    scenario = TestScenario(
        id="test_001",
        name="Test",
        category=ScenarioCategory.FILE_OPS,
        prompt=Prompt(user_query="Read file.txt"),
        expected_behavior=ExpectedBehavior(required_tools=["read_file"]),
    )
    
    messages = runner._build_messages(scenario, system_prompt="You are a helpful assistant")
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are a helpful assistant"

