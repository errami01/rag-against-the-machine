from openai import OpenAI

from student.generation.backend import LLMBackend


class VLLMBackend(LLMBackend):
    """An inference gateway interface for interacting with a localized vLLM.

    This class overrides the abstract base LLMBackend configuration,
    leveraging an OpenAI-compatible client profile to communicate with an
    isolated, locally self-hosted vLLM instance. It enforces system-level
    prompting rules optimized for strict context grounding tasks.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/v1",
        model: str = "Qwen/Qwen3-0.6B",
    ) -> None:
        """Initializes the backend interface client link pointing to the local
          engine pool.

        Args:
            base_url: The full network target address hosting the vLLM server
              endpoint stack. Defaults to "http://localhost:8000/v1".
            model: The exact text string tag mapping the targeted active model
              checkpoint
              loaded on the server node. Defaults to "Qwen/Qwen3-0.6B".
        """
        self.client = OpenAI(
            base_url=base_url,
            api_key="EMPTY",
        )

        self.model = model

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 128,
    ) -> str:
        """Submits an inference request message sequence and retrieves the
        generated response.

        Constructs a structured chat payload containing a restrictive
        system-level guideline alongside the user prompt. It executes
        greedy sampling configurations to minimize hallucination metrics
        across RAG tracking loops.

        Args:
            prompt: The formatted input instruction context containing query
            and reference sources.
            max_new_tokens: The maximum generation length bounds assigned
            for the response token generation budget. Defaults to 128.

        Returns:
            A cleaned, stripped natural language text string produced by the
            generation model.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Answer only using the provided context."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
            max_tokens=max_new_tokens,
        )
        if not response.choices or not response.choices[0].message.content:
            raise ValueError("No response generated from the model.")
        return response.choices[0].message.content.strip()
