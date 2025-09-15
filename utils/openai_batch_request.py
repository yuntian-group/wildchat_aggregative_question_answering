import os
import json
import time
import openai
import datetime
import tiktoken
from tqdm import tqdm
from typing import List
from collections import deque
import signal
import threading


class OpenAIBatchRequest:
    def __init__(
        self,
        file_name_list: List[str],
        api_key: str,
        rpm_limit: int = -1,
        tpm_limit: int = -1,
        tokenizer_encoding: str = "o200k_base",
    ):
        self._file_name_list = file_name_list
        self._tokenizer = tiktoken.get_encoding(tokenizer_encoding)
        self._open_ai_client = openai.OpenAI(api_key=api_key)
        self._task_queue = deque()
        self._rpm_limit = rpm_limit
        self._tpm_limit = tpm_limit
        self._batch_obj_list = []
        for file_name in self._file_name_list:
            if not os.path.exists(file_name):
                raise FileNotFoundError(f"File {file_name} does not exist")
            if not file_name.endswith(".jsonl") and not file_name.endswith(".json"):
                raise ValueError("Only .jsonl or .json files are supported")
            if file_name.find("batch_input") == -1:
                raise ValueError("File name should contain 'batch_input'")

    def signal_handler(self, sig, frame):
        print("Caught signal")
        for batch_obj in self._batch_obj_list:
            if self._open_ai_client.batches.retrieve(batch_obj.id).status in {
                "in_progress",
                "validating",
            }:
                print(f"Canceling batch {batch_obj.id}")
                self._open_ai_client.batches.cancel(batch_obj.id)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        exit(1)

    def do_parallel_online_and_wait(self):

        if self._rpm_limit == -1 or self._tpm_limit == -1:
            raise ValueError("RPM and TPM limit should be set")

        for file_name in self._file_name_list:
            if not os.path.exists(file_name):
                raise FileNotFoundError(f"File {file_name} does not exist")
            if not file_name.endswith(".jsonl") and not file_name.endswith(".json"):
                raise ValueError("Only .jsonl or .json files are supported")
            if file_name.find("batch_input") == -1:
                raise ValueError("File name should contain 'batch_input'")
            output_file_name = file_name.replace("batch_input", "batch_output", -1)

            cur_batch_requests = []
            cur_batch_custom_ids = []
            cur_token_counts = []

            print(f"Processing file {file_name}")
            for line in tqdm(open(file_name, "r")):
                cur = json.loads(line)
                cur_batch_requests.append(cur["body"])
                cur_batch_custom_ids.append(cur["custom_id"])
                token_count = 0
                for message in cur["body"]["messages"]:
                    token_count += len(self._tokenizer.encode(message["content"]))
                cur_token_counts.append(token_count + 504)

            # List to hold threads and responses.
            threads = []
            responses = [None] * len(cur_batch_requests)

            def worker(i, request):
                response = self._open_ai_client.chat.completions.create(**request)
                responses[i] = response

            for i in tqdm(range(len(cur_batch_requests)), desc="Requesting"):
                while True:
                    cur_time = time.time()
                    tmp_request_count = 0
                    tmp_token_count = 0

                    for j in range(len(self._task_queue) - 1, -1, -1):
                        if cur_time - self._task_queue[j][0] <= 65:
                            tmp_request_count += 1
                            tmp_token_count += self._task_queue[j][1]
                        else:
                            break

                    if (
                        tmp_request_count < self._rpm_limit
                        and tmp_token_count < self._tpm_limit * 0.75
                    ):
                        break

                thread = threading.Thread(
                    target=worker, args=(i, cur_batch_requests[i])
                )
                thread.start()
                self._task_queue.append((time.time(), cur_token_counts[i]))
                threads.append(thread)

            cur_time = time.time()
            while (
                len(self._task_queue) > 0 and (cur_time - self._task_queue[0][0]) > 65
            ):
                self._task_queue.popleft()

            print("Request {} completed".format(file_name))

            for thread in tqdm(threads, desc="Writing"):
                thread.join()

            with open(output_file_name, "w") as f:
                for i, response in enumerate(responses):
                    f.write(
                        json.dumps(
                            {
                                "response": {"body": response.to_dict()},
                                "custom_id": cur_batch_custom_ids[i],
                            }
                        )
                        + "\n"
                    )
            print(f"File {file_name} completed")

    def do_online_and_wait(self):
        for file_name in self._file_name_list:
            if not os.path.exists(file_name):
                raise FileNotFoundError(f"File {file_name} does not exist")
            if not file_name.endswith(".jsonl") and not file_name.endswith(".json"):
                raise ValueError("Only .jsonl or .json files are supported")
            if file_name.find("batch_input") == -1:
                raise ValueError("File name should contain 'batch_input'")
            output_file = file_name.replace("batch_input", "batch_output", -1)
            f = open(output_file, "w")
            print(f"Processing file {file_name}")
            for line in tqdm(open(file_name, "r")):
                request = json.loads(line)
                request_body = request["body"]
                try:
                    retry = 5
                    while retry > 0:
                        try:
                            response = self._open_ai_client.chat.completions.create(
                                **request_body
                            )
                            break
                        except Exception as e:
                            print(f"Error: {e}")
                            retry -= 1
                            time.sleep(30)
                            response = None
                except Exception as e:
                    print(f"Error: {e}")
                    response = None
                f.write(
                    json.dumps(
                        {
                            "response": {"body": response.to_dict()},
                            "custom_id": request["custom_id"],
                        }
                    )
                    + "\n"
                )
            f.close()

    def do_batch_and_wait(self, end_point="/v1/chat/completions"):

        signal.signal(signal.SIGINT, self.signal_handler)

        for file_name in self._file_name_list:
            print(f"Processing file {file_name}")
            batch_input = self._open_ai_client.files.create(
                file=open(file_name, "rb"), purpose="batch"
            )

            batch_input_file_id = batch_input.id

            batch_obj = self._open_ai_client.batches.create(
                input_file_id=batch_input_file_id,
                endpoint=end_point,
                completion_window="24h",
                metadata={"description": "Batch data annotation"},
            )
            print(batch_obj.id)
            self._batch_obj_list.append(batch_obj)

        print("Start waiting for batch to complete")
        finished = [False for _ in range(len(self._batch_obj_list))]

        while True:
            cnt = 0
            for idx, batch_obj in enumerate(self._batch_obj_list):
                if not finished[idx]:
                    batch_obj = self._open_ai_client.batches.retrieve(batch_obj.id)
                    print(datetime.datetime.now())
                    print(batch_obj.status)
                    print(batch_obj.to_dict())
                    if batch_obj.status == "completed":
                        print("Batch {} completed".format(idx))
                        output_file_response = self._open_ai_client.files.content(
                            batch_obj.output_file_id
                        )
                        json_data = output_file_response.content.decode("utf-8")
                        output_file = self._file_name_list[idx].replace(
                            "batch_input", "batch_output", -1
                        )
                        with open(output_file, "w") as f:
                            f.write(json_data)
                        finished[idx] = True
                        cnt += 1
                        f.close()

                    elif batch_obj.status == "failed":
                        print("Batch {} failed".format(idx))
                        finished[idx] = True
                        cnt += 1
                else:
                    cnt += 1
            if cnt == len(self._batch_obj_list):
                print("All batch completed")
                break
            time.sleep(20)


class OpenAIBatchRequestWithFileProcessing:
    def __init__(
        self,
        output_path: str,
        api_key: str,
        chunk_size: int = 2000,
        rpm_limit: int = -1,
        tpm_limit: int = -1,
        tokenizer_encoding: str = "o200k_base",
    ):
        self._api_key = api_key
        self._rpm_limit = rpm_limit
        self._tpm_limit = tpm_limit
        self._tokenizer_encoding = tokenizer_encoding
        self._output_path = output_path
        self._chunk_size = chunk_size

    def do_batch_request(
        self,
        requests: List[dict],
        end_point="/v1/chat/completions",
        is_debug: bool = False,
    ):

        os.makedirs(self._output_path, exist_ok=True)

        num_file = len(requests) // self._chunk_size
        if len(requests) % self._chunk_size != 0:
            num_file += 1

        all_output_file_path = []
        all_output_fild_fd = []

        for i in range(num_file):

            time_string = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

            output_file_path = os.path.join(
                self._output_path, f"batch_input_{i}_{time_string}.jsonl"
            )
            all_output_file_path.append(output_file_path)
            all_output_fild_fd.append(open(output_file_path, "w"))

        for i in range(len(requests)):
            cur_file_idx = i % num_file
            all_output_fild_fd[cur_file_idx].write(json.dumps(requests[i]) + "\n")

        for i in range(num_file):
            all_output_fild_fd[i].close()

        openai_batch_request = OpenAIBatchRequest(
            file_name_list=all_output_file_path,
            api_key=self._api_key,
            rpm_limit=self._rpm_limit,
            tpm_limit=self._tpm_limit,
            tokenizer_encoding=self._tokenizer_encoding,
        )

        if not is_debug:
            openai_batch_request.do_batch_and_wait(end_point=end_point)


def parse_single_json_respone(resp_json_str):
    data = json.loads(resp_json_str)
    hash = data["custom_id"]
    model_resp = data["response"]["body"]["choices"][0]["message"]["content"]
    model_resp = model_resp.replace("```json", "", -1)
    model_resp = model_resp.replace("```", "", -1)
    return hash, model_resp


def parse_single_embedding_response(resp_json_str):
    data = json.loads(resp_json_str)
    hash_value = data["custom_id"]
    try:
        embedding = data["response"]["body"]["data"][0]["embedding"]
    except:
        embedding = None
    return hash_value, embedding
