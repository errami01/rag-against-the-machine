from abc import ABC, abstractmethod


class LLMBackend(ABC):
    """An abstract base class defining standard language model interfaces.

    Serves as the blueprint component for all integrated text generation
    backends, ensuring consistent contract methods across varying modeling
    architectures.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 128,
    ) -> str:
        """Generate a natural language text response from an input prompt.

        Args:
            prompt: The formatted instruction string submitted to the model.
            max_new_tokens: The absolute upper token generation cutoff limit
              assigned for the output text window. Defaults to 128.

        Returns:
            The raw text string produced by the inference execution sequence.
        """
        pass
