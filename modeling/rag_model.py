import os
import json
import logging
import datasets
from typing import Tuple
from modeling.batch_inference_model import BatchInferenceModel


def build_single_prompt(
    data_sample,
    prompt_template: str,
    tokenize_func: callable,
    max_token_count: int,
    topk: int,
):
    cur_question = data_sample["question"]
    cur_options = data_sample["options"]

    if "context" in data_sample:
        cur_context_list = data_sample["context"]
    else:
        cur_context_list = []

    cur_options_string = ""
    for j, option in enumerate(cur_options):
        cur_options_string += f"{j}. {option}\n"
    cur_question_string = f"{cur_question}\n{cur_options_string}"

    prompt1 = prompt_template.replace("{{question}}", cur_question_string)

    cur_context = ""
    token_count = len(tokenize_func(prompt1)) - len(tokenize_func("{{conversations}}"))
    for i in range(min(len(cur_context_list), topk)):
        cur_doc_token = len(tokenize_func(cur_context_list[i]))
        if token_count + cur_doc_token >= max_token_count:
            print("Failed to reach topk {} with max token count".format(topk))
            break
        cur_context += cur_context_list[i] + "\n\n"
        token_count += cur_doc_token

    if cur_context is not None:
        prompt2 = prompt1.replace("{{conversations}}", cur_context)
    else:
        prompt2 = prompt1

    return {
        "custom_id": data_sample["hash"],
        "prompt": prompt2,
        "token_count_prompt": token_count,
    }


class RetrieverBase:
    def __init__(
        self,
        rag_type: str,
        data_path: str,
        prompt_template_path: str,
        tokenize_func: callable,
        max_context_token_count: int = 1048576,
        save_request: bool = False,
        save_context: bool = False,
        data_parallel: int = 1,
        data_parallel_rank: int = 0,
    ):
        self.rag_type = rag_type
        with open(prompt_template_path, "r") as f:
            self.prompt_template = f.read()
        self.dataset = datasets.Dataset.load_from_disk(data_path)

        if data_parallel > 1:
            cur_index = list(
                range(data_parallel_rank, len(self.dataset), data_parallel)
            )
            self.dataset = self.dataset.select(cur_index)

        self.tokenize_func = tokenize_func
        self.max_context_token_count = max_context_token_count
        self.save_request = save_request
        self.save_context = save_context
        self.data_parallel = data_parallel
        self.data_parallel_rank = data_parallel_rank

    def build_context(self, data: datasets.Dataset) -> str:
        raise NotImplementedError()


class RAGModel:
    def __init__(
        self,
        logging_path: str,
        retrieve_context_path: str,
        logger: logging.Logger,
        model: BatchInferenceModel = None,
        retriever: RetrieverBase = None,
    ):

        self.model = model
        self.retriever = retriever
        self.logger = logger
        self.logging_path = logging_path
        self.retrieve_context_path = retrieve_context_path

    def build_prompt(self, dataset_with_context: datasets.Dataset) -> Tuple[str, int]:
        return dataset_with_context.map(
            build_single_prompt,
            fn_kwargs={
                "prompt_template": self.retriever.prompt_template,
                "tokenize_func": self.retriever.tokenize_func,
                "max_token_count": self.retriever.max_context_token_count,
                "topk": self.retriever.topk,
            },
            remove_columns=dataset_with_context.column_names,
            num_proc=min(os.cpu_count(), 8),
            desc="Building prompts",
        )

    def run_context_build(self, build_prompt: bool = True):

        if self.retriever is None:
            raise ValueError("No retriever found")

        if os.path.exists(self.retrieve_context_path):
            self.logger.info(f"Loading context from {self.retrieve_context_path}")
            dataset_with_context = datasets.Dataset.load_from_disk(
                self.retrieve_context_path
            )

            if self.retriever.data_parallel > 1:
                self.logger.info(
                    f"RAG MODEL Filtering context for data parallel rank {self.retriever.data_parallel_rank}"
                )

                cur_idx = list(
                    range(
                        self.retriever.data_parallel_rank,
                        len(dataset_with_context),
                        self.retriever.data_parallel,
                    )
                )
                dataset_with_context = dataset_with_context.select(cur_idx)

            # if len(dataset_with_context) != len(self.retriever.dataset):
            #     all_hashes = set(self.retriever.dataset["hash"])
            #     dataset_with_context = dataset_with_context.filter(
            #         lambda x: x["hash"] in all_hashes
            #     )
            assert len(dataset_with_context) == len(
                self.retriever.dataset
            ), "The context dataset must have the same number of samples as the original dataset."
        else:
            dataset_with_context = self.retriever.build_context(self.retriever.dataset)
            dataset_with_context.save_to_disk(self.retrieve_context_path)

        if not build_prompt:
            return []

        prompts = self.build_prompt(dataset_with_context)
        total_token_count_prompt = sum(prompts["token_count_prompt"])

        self.logger.info(f"Total token count for prompts: {total_token_count_prompt}")

        if self.retriever.save_request:
            p = f"{self.logging_path}/request.json"
            self.logger.info(f"Writing prompts to file {p}")
            with open(p, "w") as f:
                for prompt in prompts:
                    f.write(json.dumps(prompt) + "\n")

            if self.retriever.rag_type != "none":
                with open(f"{self.logging_path}/retrieved_doc_ids.json", "w") as f:
                    for i in range(len(prompts)):
                        f.write(
                            json.dumps(
                                {
                                    "hash": dataset_with_context[i]["hash"],
                                    "context_doc_ids": dataset_with_context[i][
                                        "context_doc_ids"
                                    ],
                                }
                            )
                            + "\n"
                        )

        return prompts

    def run_get_responses(self, prompts):
        if self.model is None:
            raise ValueError("No model found")

        response = self.model.get_responses(prompts)
        with open(f"{self.logging_path}/response.json", "w") as f:
            for r in response:
                f.write(json.dumps(r) + "\n")

        return response

    def run_full(self):
        prompts = self.run_context_build()
        response = self.run_get_responses(prompts)

        return response
