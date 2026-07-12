from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer, PreTrainedTokenizerBase)
from student.generation.backend import LLMBackend
from typing import Any


MODEL_NAME = "Qwen/Qwen3-0.6B"


class TransformersBackend(LLMBackend):
    """A singleton gateway interface for running a localized model.

    This class overrides the abstract base LLMBackend configuration,
    leveraging a single in-memory model instance across the pipeline
    process to avoid redundant GPU memory allocations.
    """
    tokenizer: PreTrainedTokenizerBase
    model: Any
    _instance: "TransformersBackend | None" = None

    def __new__(cls) -> 'TransformersBackend':
        """Create and initialize the singleton model and tokenizer instance.
        """
        if cls._instance is None:

            cls._instance = super().__new__(cls)

            cls._instance.tokenizer = (
                AutoTokenizer.from_pretrained(
                    MODEL_NAME
                )
            )

            cls._instance.model = (
                AutoModelForCausalLM.from_pretrained(
                    MODEL_NAME,
                    torch_dtype="auto",
                    device_map="auto",
                )
            )

        return cls._instance

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 1000,
    ) -> str:
        """Generate a contextual solution from a Hugging Face model template.

        Applies a structural chat template to bind restrictive assistant goals,
        prepares tensor blocks for the current active device mapping layout,
        and enforces greedy decoding variables to optimize deterministic
          answers.

        Args:
            prompt: The text instruction context containing user query data.
            max_new_tokens: The absolute upper token generation allocation
                depth. Defaults to 300.

        Returns:
            The raw text string answer cleared of input padding and system
            special tokens.
        """

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert assistant for the vLLM project."
                    "Answer from the context."
                    "Answer in json."
                    "Fill the template below"
                    '{'
                    '   "answer": "<Detailed Answer>",'
                    '   "source_id": ""'
                    '}'
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False
        )
        inputs: dict[str, Any] = self.tokenizer(
            text,
            return_tensors="pt",
        ).to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=None,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        # outputs = self.model.generate(
        #     **inputs,
        #     max_new_tokens=max_new_tokens,
        #     do_sample=False,
        # )

        generated = outputs[0][inputs["input_ids"].shape[1]:]
        decoded_text = self.tokenizer.decode(
            generated,
            skip_special_tokens=True
            )

        if isinstance(decoded_text, list):
            decoded_text = " ".join(decoded_text)

        return decoded_text.strip()

    @classmethod
    def get_instance(cls) -> 'TransformersBackend':
        """Retrieve or construct the global shared backend client state
          instance.

        Returns:
            The active instantiated runtime object representing the singleton.
        """
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance
