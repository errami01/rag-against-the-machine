from openai import OpenAI

from student.generation.backend import LLMBackend


class VLLMBackend(LLMBackend):

    def __init__(
        self,
        base_url: str = "http://localhost:8000/v1",
        model: str = "Qwen/Qwen3-0.6B",
    ) -> None:

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

        return response.choices[0].message.content.strip()