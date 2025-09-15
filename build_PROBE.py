import os
import yaml
import json
import tiktoken
import argparse
import datasets
import numpy as np
from typing import Dict, List
from utils.logging_utils import init_logger
from utils.utils import parse_embedding_output
from modeling import build_model, build_tokenizer
from utils.openai_batch_request import OpenAIBatchRequestWithFileProcessing

EMBEDDING_TOKENIZER = tiktoken.get_encoding("cl100k_base")


def build_request(data, prompt_template: str, tokenize_func: callable):
    all_questions = data["question"]
    all_hash_ids = data["hash"]

    all_prompts = []
    all_token_counts = []

    for i in range(len(all_questions)):
        question = all_questions[i]
        x = prompt_template.replace("{{question}}", question)
        all_prompts.append(x)
        all_token_counts.append(len(tokenize_func(x)))
    return {
        "prompt": all_prompts,
        "custom_id": all_hash_ids,
        "token_count": all_token_counts,
    }


def generate_query(config: Dict, log_path: str, dataset: datasets.Dataset):

    with open(args.prompt_path, "r") as f:
        prompt_template = f.read()

    assert (
        "query_generation_model_config" in config
    ), "No query generation model config found in config file"

    model_config = config["query_generation_model_config"]
    tokenize_func, chat_template_func = build_tokenizer(model_config)

    requests = dataset.map(
        build_request,
        fn_kwargs={"prompt_template": prompt_template, "tokenize_func": tokenize_func},
        batched=True,
        remove_columns=dataset.column_names,
    )

    print(f"Loaded {len(requests)} requests")
    print(f"Total token count: {sum(requests['token_count'])}")

    model = build_model(
        {
            "chat_template_func": chat_template_func,
            "logging_path": log_path,
            **model_config,
        }
    )

    response = model.get_responses(requests)

    ret = []

    with open(
        f"{log_path}/responses.json",
        "w",
    ) as f:
        for r in response:
            tmp = json.dumps(r)
            f.write(tmp + "\n")
            ret.append(tmp)
    return ret


def merge_to_dataset(response: List[str], dataset: datasets.Dataset):
    all_hash = dataset["hash"]
    hash_to_generated_query = {}
    for r in response:
        try:
            d = json.loads(r)
            cid = d["custom_id"]
            hash_to_generated_query[cid] = d["response"]
        except Exception as e:
            print(f"Error parsing response merge: {e}")

    generated_queries_column = []
    for i in range(len(all_hash)):
        cur_hash = all_hash[i]
        if cur_hash not in hash_to_generated_query:
            generated_queries_column.append("")
        else:
            generated_queries_column.append(hash_to_generated_query[cur_hash])
    dataset = dataset.add_column("generated_query", generated_queries_column)
    return dataset


def merge_generated_query_embedding_to_dataset(
    dataset: datasets.Dataset,
    output_path: str,
    max_embedding_per_question: int = 10,
    embedding_dim: int = 3072,
):
    all_hash = dataset["hash"]

    hash_to_index = {}
    for i in range(len(all_hash)):
        cur_hash = all_hash[i]
        hash_to_index[cur_hash] = i

    all_embeddings = [
        np.zeros((max_embedding_per_question, embedding_dim), dtype=np.float16)
        for _ in range(len(all_hash))
    ]
    all_embedding_success_flag = [
        [0 for _ in range(max_embedding_per_question)] for _ in range(len(all_hash))
    ]

    hash_to_embedding = parse_embedding_output(output_path)

    for h in hash_to_embedding:
        real_hash, embedding_index = h.split("_")

        embedding_index = int(embedding_index)
        if embedding_index >= max_embedding_per_question:
            print(
                f"Embedding index {embedding_index} exceeds max embedding per question {max_embedding_per_question}"
            )
            continue
        real_index = hash_to_index[real_hash]
        all_embeddings[real_index][embedding_index] = hash_to_embedding[h]
        all_embedding_success_flag[real_index][embedding_index] = 1

    dataset = dataset.add_column(
        "query_embeddings", [x.tolist() for x in all_embeddings]
    )
    dataset = dataset.add_column(
        "query_embedding_success_flag", all_embedding_success_flag
    )
    return dataset


def build_query_embedding(config: Dict, log_path: str, dataset):
    query_generation_model_config = config["query_generation_model_config"]
    max_embedding_per_question = query_generation_model_config.get(
        "max_embedding_per_question", 10
    )
    query_embedding_model = query_generation_model_config.get(
        "query_embedding_model", "text-embedding-3-large"
    )
    embedding_dim = query_generation_model_config.get("embedding_dim", 3072)
    all_generated_queries = dataset["generated_query"]
    all_hash = dataset["hash"]

    generated_query_with_hash = []
    for i in range(len(all_generated_queries)):
        try:
            generated_hybrid_query = json.loads(all_generated_queries[i])["query"]
            all_queries = generated_hybrid_query.get("queries", [])
            cur_question_hash = all_hash[i]
            for qidx, query in enumerate(all_queries):
                generated_query_with_hash.append(
                    {
                        "query": query,
                        "hash": cur_question_hash + "_" + str(qidx),
                    }
                )
        except Exception as e:
            print(
                f"Error parsing response query: {e}, {all_hash[i]}, {all_generated_queries[i]}"
            )

    all_requests = []
    all_token_counts = []

    for i in range(len(generated_query_with_hash)):
        cur_query = generated_query_with_hash[i]["query"]
        req = {
            "custom_id": generated_query_with_hash[i]["hash"],
            "method": "POST",
            "url": "/v1/embeddings",
            "body": {
                "input": cur_query,
                "model": query_embedding_model,
                "encoding_format": "float",
            },
        }
        all_requests.append(req)
        all_token_counts.append(len(EMBEDDING_TOKENIZER.encode(cur_query)))

    output_path = os.path.join(log_path, "generated_query_embedding")

    print(f"Loaded {len(all_requests)} requests")
    print(f"Total token count: {sum(all_token_counts)}")

    requestor = OpenAIBatchRequestWithFileProcessing(
        output_path, os.environ["OPENAI_API_KEY"]
    )
    requestor.do_batch_request(all_requests, "/v1/embeddings")

    return merge_generated_query_embedding_to_dataset(
        dataset,
        output_path,
        max_embedding_per_question=max_embedding_per_question,
        embedding_dim=embedding_dim,
    )


def main(args):
    with open(args.config_path, "r") as f:
        config = yaml.safe_load(f)
        rag_config = config["rag_config"]
        rag_type = rag_config["rag_type"]

    log_path, logger = init_logger(
        config_path=args.config_path,
    )

    d = datasets.Dataset.load_from_disk(rag_config["data_path"])
    all_generated_queries = generate_query(config, log_path, d)
    dataset = merge_to_dataset(all_generated_queries, d)
    dataset.save_to_disk(os.path.join(log_path, "dataset_with_generated_query"))
    final_dataset = build_query_embedding(config, log_path, dataset)
    final_dataset.save_to_disk(
        os.path.join(log_path, "dataset_with_generated_query_and_embedding")
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config_path",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--prompt_path",
        type=str,
        default="prompts/build_probe_request.md",
    )
    datasets.disable_caching()
    args = parser.parse_args()
    main(args)
