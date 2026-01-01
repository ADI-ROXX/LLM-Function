from .models import LLMConfig, LLMProvider
from .base_runner import BaseLLMRunner
from .deepseek_runner import DeepseekRunner
from .ollama_runner import OllamaRunner


class RunnerFactory:
    @staticmethod
    def create_runner(config: LLMConfig) -> BaseLLMRunner:
        if config.provider == LLMProvider.DEEPSEEK:
            return DeepseekRunner(config)
        elif config.provider == LLMProvider.OLLAMA:
            return OllamaRunner(config)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")

    @staticmethod
    def create_deepseek_runner(
        model: str = "deepseek-chat",
        api_key: str = None,
        temperature: float = 0.7,
        max_tokens: int = None,
    ) -> DeepseekRunner:
        config = LLMConfig(
            provider=LLMProvider.DEEPSEEK,
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return DeepseekRunner(config)

    @staticmethod
    def create_ollama_runner(
        model: str = "llama3.2:1b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
    ) -> OllamaRunner:
        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model=model,
            base_url=base_url,
            temperature=temperature,
        )
        return OllamaRunner(config)

