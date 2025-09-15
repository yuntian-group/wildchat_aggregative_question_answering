import vllm
from tqdm import tqdm
from typing import List
from modeling.batch_inference_model import BatchInferenceModel


class VLLMBatchInferenceModel(BatchInferenceModel):
    def __init__(
        self,
        name: str,
        chat_template_func: callable,
        logging_path: str,
        sampling_params: dict,
        batch_size: int,
        tensor_parallel_size: int = 1,
        rope_scaling: dict = {},
        **kwargs,
    ):
        super().__init__()
        self.llm = vllm.LLM(
            model=name,
            trust_remote_code=True,
            tensor_parallel_size=tensor_parallel_size,
            rope_scaling=rope_scaling if rope_scaling else None,
            dtype="bfloat16" if name.find("gemma-3") != -1 else "auto",
        )
        self.sampling_params = vllm.SamplingParams(**sampling_params)
        self.chat_template_func = chat_template_func
        self.logging_path = logging_path
        self.batch_size = batch_size

    def get_responses(self, prompts: List):

        ret = []

        prompt_with_template = []

        for i, prompt in enumerate(tqdm(prompts, desc="Applying chat template")):
            prompt_with_template.append(
                self.chat_template_func([{"role": "user", "content": prompt["prompt"]}])
            )

        for i in range(0, len(prompt_with_template), self.batch_size):
            cur_batch = prompt_with_template[i : i + self.batch_size]
            outputs = self.llm.generate(cur_batch, self.sampling_params)
            for idx, output in enumerate(outputs):
                cur_idx = i + idx
                ret.append(
                    {
                        "custom_id": prompts[cur_idx]["custom_id"],
                        "response": output.outputs[0].text,
                    }
                )
        return ret
