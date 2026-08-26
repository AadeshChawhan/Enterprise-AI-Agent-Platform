from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def model_available(
        self,
        model: str
    ) -> bool:
        pass

    @abstractmethod
    def generate_response(
        self,
        prompt: str,
        model: str,
        temperature: float,
        messages: list | None = None,
        system_prompt: str = "",
    ):
        pass

    @abstractmethod
    def stream_response(
        self,
        prompt: str,
        model: str,
        temperature: float,
        messages: list | None = None,
        system_prompt: str = "",
    ):
        pass

    @abstractmethod
    def generate_conversation_title(
        self,
        prompt: str,
        model: str,
    ) -> str:
        pass

    @abstractmethod
    def list_models(self) -> list[str]:
        pass