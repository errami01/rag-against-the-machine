from abc import ABC, abstractmethod


class LLMBackend(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 128,
    ) -> str:
        pass