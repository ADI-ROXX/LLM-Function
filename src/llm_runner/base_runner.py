from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .models import LLMConfig, LLMResponse
from src.scenario_engine.models import TestScenario
from src.tool_system.models import Tool


class BaseLLMRunner(ABC):
    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    def run(
        self,
        scenario: TestScenario,
        tools: List[Tool],
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        pass

    @abstractmethod
    def run_with_messages(
        self,
        messages: List[Dict[str, str]],
        tools: List[Tool],
    ) -> LLMResponse:
        pass

    def _build_messages(
        self,
        scenario: TestScenario,
        system_prompt: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if scenario.prompt.context:
            messages.append({"role": "system", "content": scenario.prompt.context})

        messages.append({"role": "user", "content": scenario.prompt.user_query})

        return messages

