import time
import json
from typing import List, Dict, Any, Optional
import requests
from .base_runner import BaseLLMRunner
from .models import LLMConfig, LLMResponse, FunctionCall, ResponseMetadata, LLMProvider
from src.scenario_engine.models import TestScenario
from src.tool_system.models import Tool
from src.tool_system.schema_generator import SchemaGenerator


class OllamaRunner(BaseLLMRunner):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"

    def run(
        self,
        scenario: TestScenario,
        tools: List[Tool],
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        messages = self._build_messages(scenario, system_prompt)
        return self.run_with_messages(messages, tools, scenario.id)

    def run_with_messages(
        self,
        messages: List[Dict[str, str]],
        tools: List[Tool],
        scenario_id: Optional[str] = None,
    ) -> LLMResponse:
        start_time = time.time()
        
        try:
            tool_schemas = SchemaGenerator.tools_to_ollama_format(tools)
            
            payload = {
                "model": self.config.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                }
            }
            
            if tool_schemas:
                payload["tools"] = tool_schemas
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.config.timeout,
            )
            
            response.raise_for_status()
            
            end_time = time.time()
            latency = (end_time - start_time) * 1000
            
            data = response.json()
            
            response_text = None
            function_calls = []
            
            message = data.get("message", {})
            
            if message.get("content"):
                response_text = message["content"]
            
            if message.get("tool_calls"):
                for idx, tool_call in enumerate(message["tool_calls"]):
                    function_calls.append(
                        FunctionCall(
                            id=tool_call.get("id"),
                            name=tool_call["function"]["name"],
                            arguments=tool_call["function"].get("arguments", {}),
                            sequence_number=idx + 1,
                        )
                    )
            
            tokens_used = None
            prompt_tokens = None
            completion_tokens = None
            
            if "prompt_eval_count" in data:
                prompt_tokens = data["prompt_eval_count"]
            if "eval_count" in data:
                completion_tokens = data["eval_count"]
            if prompt_tokens and completion_tokens:
                tokens_used = prompt_tokens + completion_tokens
            
            metadata = ResponseMetadata(
                latency_ms=latency,
                tokens_used=tokens_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                model=self.config.model,
            )
            
            return LLMResponse(
                scenario_id=scenario_id,
                provider=LLMProvider.OLLAMA,
                model=self.config.model,
                response_text=response_text,
                function_calls=function_calls,
                metadata=metadata,
                raw_response=data,
            )
            
        except Exception as e:
            end_time = time.time()
            latency = (end_time - start_time) * 1000
            
            metadata = ResponseMetadata(
                latency_ms=latency,
                model=self.config.model,
            )
            
            return LLMResponse(
                scenario_id=scenario_id,
                provider=LLMProvider.OLLAMA,
                model=self.config.model,
                metadata=metadata,
                error=str(e),
            )

