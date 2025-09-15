import os
import glob
import json
import openai
import datasets
from tqdm import tqdm
from typing import List
from utils.openai_batch_request import OpenAIBatchRequest
from modeling.batch_inference_model import BatchInferenceModel


class OpenAIBatchRequestModel(BatchInferenceModel):
    def __init__(
        self,
        name: str,
        chat_template_func: callable,
        sampling_params: dict,
        batch_size: int,
        logging_path: str,
        rpm_limit: int,
        tpm_limit: int,
        request_mode: str = "offline_batch",
        **kwargs,
    ):
        self.name = name
        self.sampling_params = sampling_params
        self.batch_size = batch_size
        self.log_path = logging_path
        self.request_mode = request_mode
        self.rpm_limit = rpm_limit
        self.tpm_limit = tpm_limit

        print("rate limit: ", self.rpm_limit, self.tpm_limit)

    def get_responses(self, prompts: datasets.Dataset) -> List[dict]:

        num_file = len(prompts) // self.batch_size

        if len(prompts) % self.batch_size != 0:
            num_file += 1

        all_file_fds = []
        all_file_names = []

        for i in range(num_file):
            cur_file_path = os.path.join(self.log_path, "batch_input_{}.json".format(i))
            all_file_names.append(cur_file_path)
            cur_fd = open(cur_file_path, "w")
            all_file_fds.append(cur_fd)

        for i, prompt in enumerate(tqdm(prompts, desc="Writing to files")):
            cur_fd = all_file_fds[i % num_file]
            msg = [{"role": "user", "content": prompt["prompt"]}]

            d = {
                "custom_id": prompt["custom_id"],
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": self.name,
                    "messages": msg,
                    **self.sampling_params,
                },
            }

            cur_fd.write(json.dumps(d) + "\n")

        for fd in all_file_fds:
            fd.close()

        req = OpenAIBatchRequest(
            all_file_names,
            os.environ["OPENAI_API_KEY"],
            rpm_limit=self.rpm_limit,
            tpm_limit=self.tpm_limit,
        )

        if self.request_mode == "online":
            req.do_online_and_wait()
        elif self.request_mode == "online_async":
            req.do_parallel_online_and_wait()
        else:
            req.do_batch_and_wait()

        all_outputs = []

        output_list = glob.glob(os.path.join(self.log_path, "batch_output_*.json"))
        for output in output_list:
            with open(output, "r") as f:
                for line in f:
                    x = json.loads(line)
                    cid = x["custom_id"]
                    resp = x["response"]["body"]["choices"][0]["message"]["content"]
                    all_outputs.append({"custom_id": cid, "response": resp})
        return all_outputs
