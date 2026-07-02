from student.generation.transformers_backend import TransformersBackend
from student.generation.vllm_backend import VLLMBackend


class BackendFactory:

    @staticmethod
    def create(name: str):

        if name == "transformers":
            return TransformersBackend()

        if name == "vllm":
            return VLLMBackend()

        raise ValueError(
            f"Unknown backend: {name}"
        )