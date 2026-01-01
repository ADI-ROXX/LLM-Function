import time
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from .base_runner import BaseLLMRunner
from .models import LLMConfig, LLMResponse, FunctionCall, ResponseMetadata, LLMProvider
from src.scenario_engine.models import TestScenario
from src.tool_system.models import Tool
from src.tool_system.schema_generator import SchemaGenerator


class DeepseekRunner(BaseLLMRunner):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        
        base_url = config.base_url or "https://api.deepseek.com"
        
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=base_url,
            timeout=config.timeout,
        )

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
            tool_schemas = SchemaGenerator.tools_to_deepseek_format(tools)
            
            kwargs = {
                "model": self.config.model,
                "messages": messages,
                "temperature": self.config.temperature,
            }
            
            if tool_schemas:
                kwargs["tools"] = tool_schemas
            
            if self.config.max_tokens:
                kwargs["max_tokens"] = self.config.max_tokens
            
            response = self.client.chat.completions.create(**kwargs)
            
            end_time = time.time()
            latency = (end_time - start_time) * 1000
            
            response_text = None
            function_calls = []
            
            message = response.choices[0].message
            
            if message.content:
                response_text = message.content
            
            if hasattr(message, "tool_calls") and message.tool_calls:
                for idx, tool_call in enumerate(message.tool_calls):
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    function_calls.append(
                        FunctionCall(
                            id=tool_call.id,
                            name=tool_call.function.name,
                            arguments=arguments,
                            sequence_number=idx + 1,
                        )
                    )
            
            tokens_used = None
            prompt_tokens = None
            completion_tokens = None
            
            if hasattr(response, "usage") and response.usage:
                tokens_used = response.usage.total_tokens
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
            
            cost = self._calculate_cost(prompt_tokens, completion_tokens)
            
            metadata = ResponseMetadata(
                latency_ms=latency,
                tokens_used=tokens_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost=cost,
                model=self.config.model,
            )
            
            return LLMResponse(
                scenario_id=scenario_id,
                provider=LLMProvider.DEEPSEEK,
                model=self.config.model,
                response_text=response_text,
                function_calls=function_calls,
                metadata=metadata,
                raw_response=response.model_dump() if hasattr(response, "model_dump") else None,
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
                provider=LLMProvider.DEEPSEEK,
                model=self.config.model,
                metadata=metadata,
                error=str(e),
            )

    def _calculate_cost(
        self,
        prompt_tokens: Optional[int],
        completion_tokens: Optional[int],
    ) -> Optional[float]:
        if prompt_tokens is None or completion_tokens is None:
            return None
        
        DEEPSEEK_PRICING = {
            "deepseek-chat": {
                "prompt": 0.14 / 1_000_000,
                "completion": 0.28 / 1_000_000,
            },
            "deepseek-reasoner": {
                "prompt": 0.55 / 1_000_000,
                "completion": 2.19 / 1_000_000,
            },
        }
        
        pricing = DEEPSEEK_PRICING.get(self.config.model, DEEPSEEK_PRICING["deepseek-chat"])
        
        cost = (prompt_tokens * pricing["prompt"]) + (completion_tokens * pricing["completion"])
        
        return cost

