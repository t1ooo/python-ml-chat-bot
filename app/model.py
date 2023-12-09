from typing import List, Optional
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


class Godel:
    def __init__(self, instruction: Optional[str] = None):
        model_name = "microsoft/GODEL-v1_1-large-seq2seq"
        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self._instruction = (
            instruction
            or "Instruction: given a dialog context and related knowledge, you need to response empathically."
        )

    def _generate(self, instruction: str, knowledge: str, messages: List[str]) -> str:
        if knowledge != "":
            knowledge = "[KNOWLEDGE] " + knowledge
        query = f"{instruction} [CONTEXT] {' EOS '.join(messages)} {knowledge}"
        input_ids = self._tokenizer.encode(f"{query}", return_tensors="pt")
        outputs = self._model.generate(
            inputs=input_ids,
            max_new_tokens=20,
            min_new_tokens=8,
            top_p=0.9,
            do_sample=True,
            repetition_penalty=5.0,
        )
        output = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
        return output

    def __call__(self, profile: str, messages: List[str]) -> str:
        return self._generate(self._instruction, profile, messages)


def echo(profile: str, messages: List[str]) -> str:
    return f"Thank you for sending me this message: {messages[-1]}"
