from student.generation.transformers_backend import TransformersBackend
from student.generation.vllm_backend import VLLMBackend


class BackendFactory:
    """A factory class for creating language model backend interfaces.

    Provides a centralized initialization point to map framework identifier
    strings to their corresponding backend execution instances.
    """

    @staticmethod
    def create(name: str):
        """Create and return a concrete language model backend instance.

        Args:
            name: The framework identifier string (e.g., "transformers"
              or "vllm").

        Returns:
            An instantiated concrete subclass of LLMBackend corresponding
            to the chosen framework name.

        Raises:
            ValueError: If the provided backend name does not match any
              supported framework implementation.
        """
        if name == "transformers":
            return TransformersBackend()

        if name == "vllm":
            return VLLMBackend()

        raise ValueError(
            f"Unknown backend: {name}"
        )
