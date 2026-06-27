from transformers import (AutoModelForCausalLM,AutoTokenizer)
import torch


MODEL_NAME = "Qwen/Qwen3-0.6B"
class QwenModel:

    _instance = None

    def __new__(cls):
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
        max_new_tokens: int = 256,
    ) -> str:

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
        ).to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )

        generated = outputs[0][
            inputs["input_ids"].shape[1]:
        ]

        return self.tokenizer.decode(
            generated,
            skip_special_tokens=True,
        ).strip()
    
    @classmethod
    def get_instance(cls) -> "QwenModel":

        if cls._instance is None:
            cls._instance = cls()

        return cls._instance