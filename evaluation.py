import os
import json
import yaml
import wandb
import random
import datasets
import argparse
from typing import Dict, List
from sklearn.metrics import f1_score, ndcg_score
from utils.logging_utils import init_logger, init_logger_simple
from utils.utils import seed_everthing, parse_response_single, TOPK_PRED
from modeling import build_model, build_retriever, build_tokenizer, RAGModel



def random_predictions(data, max_choice: int):
    all_choices = list(range(len(data["options"])))
    random.shuffle(all_choices)
    to_choose = random.randint(1, max_choice)
    data["prediction"] = all_choices[:to_choose]
    return data


def ground_truth_prediction(data, max_choice: int):
    topk_index = sorted(
        range(len(data["option_weights"])),
        key=lambda x: data["option_weights"][x],
        reverse=True,
    )[:max_choice]

    to_choose = []
    for i in range(len(topk_index)):
        if data["option_weights"][topk_index[i]] > 0:
            to_choose.append(topk_index[i])

    data["prediction"] = to_choose
    return data


def compute_subset_metrics(predictions, labels, labels_binary):
    label_vector_weighted = labels
    fake_cross_entropy = 0.0
    for i in range(len(label_vector_weighted)):
        for j in range(len(label_vector_weighted[i])):
            fake_cross_entropy += label_vector_weighted[i][j] * predictions[i][j]

    fake_cross_entropy /= len(label_vector_weighted)
    mico_f1 = f1_score(labels_binary, predictions, average="micro")
    macro_f1 = f1_score(labels_binary, predictions, average="macro")
    return {
        "micro_f1": mico_f1,
        "macro_f1": macro_f1,
        "fake_cross_entropy": fake_cross_entropy,
    }


def compute_metrics_ndcg(
    predictions_full, labels_full, metadata=None, slient=False, f1_topk: int = 5
):

    return {
        "ndcg_1": ndcg_score(labels_full, predictions_full, k=1),
        "ndcg_3": ndcg_score(labels_full, predictions_full, k=3),
        "ndcg_5": ndcg_score(labels_full, predictions_full, k=5),
        "ndcg_10": ndcg_score(labels_full, predictions_full, k=10),
    }


def compute_metrics(
    predictions_full, labels_full, metadata=None, slient=False, f1_topk: int = 5
):
    label_vector_binary = []
    prediction_vectors_score = []
    prediction_vectors_list = []

    for i in range(len(labels_full)):

        cur_pred_score = [0.0 for _ in range(len(labels_full[i]))]
        cur_score = 9.0

        for item in predictions_full[i]:

            if item >= len(labels_full[i]):
                print("error {}".format(item))
                continue

            cur_pred_score[item] = cur_score
            cur_score -= 1.0
        prediction_vectors_score.append(cur_pred_score)

        topk_index = sorted(
            range(len(labels_full[i])),
            key=lambda x: labels_full[i][x],
            reverse=True,
        )[:f1_topk]
        label_vector_binary.append([0.0] * len(labels_full[i]))
        for index in topk_index:
            if labels_full[i][index] > 0:
                label_vector_binary[i][index] = 1.0

        prediction_vectors = [0.0] * len(labels_full[i])
        for index in predictions_full[i]:
            if index < len(prediction_vectors):
                prediction_vectors[index] = 1.0
            else:
                if not slient:
                    print("Invalid index", index, len(prediction_vectors))
        prediction_vectors_list.append(prediction_vectors)

    binary_metrics = compute_subset_metrics(
        prediction_vectors_list, labels_full, label_vector_binary
    )
    ndcg_metrics = compute_metrics_ndcg(
        prediction_vectors_score, labels_full, metadata, slient, f1_topk
    )

    return {
        **binary_metrics,
        **ndcg_metrics,
    }


def init_wandb_logger(config):
    model_name = config["model_config"]["name"]
    topk = config["rag_config"].get("topk", 0)
    rag_type = config["rag_config"].get("rag_type", "none")
    is_summary_bool = (
        config["rag_config"].get("prompt_template_path", "").find("summary") != -1
    )
    is_thinking_bool = config["model_config"].get("enable_thinking", False)

    is_summary_str = "raw"
    is_model_generated_str = "retrieve"
    if is_summary_bool:
        is_summary_str = "summary"
    is_model_generated_query = "query_generation_model_config" in config
    if is_model_generated_query:
        is_model_generated_str = "retrieve_model_generated"

    run_name = (
        model_name
        + "_"
        + str(topk)
        + "_"
        + is_summary_str
        + "_"
        + is_model_generated_str
        + "_"
        + rag_type
    )

    if is_thinking_bool:
        run_name += "_thinking"

    wandb.init(
        project="wildchat_aqa",
        config={
            "model_name": model_name,
            "topk": config["rag_config"].get("topk", 0),
            "rag_type": rag_type,
            "is_summary": is_summary_bool,
            "is_model_generated_query": "query_generation_model_config" in config,
            "is_thinking": is_thinking_bool,
        },
        name=run_name,
    )


def get_retrieve_cache_path(config: Dict):
    rag_type = config["rag_config"].get("rag_type", "none")
    data_path = config["rag_config"].get("data_path", "")
    is_summary_bool = (
        config["rag_config"].get("prompt_template_path", "").find("summary") != -1
    )
    is_model_generated_query_bool = "query_generation_model_config" in config

    is_force_question_query = config["rag_config"].get("force_question_query", False)
    is_force_no_query = config["rag_config"].get("force_no_query", False)

    is_summary_str = "raw"
    if is_summary_bool:
        is_summary_str = "summary"

    is_model_generated_str = "retrieve"
    if is_model_generated_query_bool:
        is_model_generated_str = "retrieve_model_generated"

    real_path = is_model_generated_str + "_" + rag_type + "_" + is_summary_str

    if is_force_no_query:
        real_path += "_force_no_query"
    if is_force_question_query:
        real_path += "_force_question_query"

    cache_path = os.path.join(data_path, real_path)
    return cache_path


def parse_response_with_hash(resp_list: List):
    id_to_answer = {}
    for model_resp in resp_list:
        cid = model_resp["custom_id"]
        cur_prediction = parse_response_single(model_resp["response"], cid)
        id_to_answer[cid] = cur_prediction
    return id_to_answer


def compute_metrics_full(model_response, dataset, logger):
    hash_to_predictions = parse_response_with_hash(model_response)
    all_hashes = dataset["hash"]
    all_options_weights = dataset["option_weights"]
    logger.info(
        f"Number of predictions: {len(hash_to_predictions)}, Number of hashes: {len(all_hashes)}, Number of option weights: {len(all_options_weights)}"
    )
    all_predictions = []
    for h in all_hashes:
        if h not in hash_to_predictions:
            logger.info(f"Hash {h} not found in predictions")
            all_predictions.append([])
        else:
            all_predictions.append(hash_to_predictions[h])
    metrics = compute_metrics(all_predictions, all_options_weights, TOPK_PRED)
    return metrics


def seed_and_load(args):
    seed_everthing(args.seed)
    log_path, logger = init_logger(args.config_path)
    with open(args.config_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    dataset = datasets.Dataset.load_from_disk(config["rag_config"]["data_path"])
    logger.info("Dataset columns: {}".format(dataset.column_names))
    logger.info("Dataset length: {}".format(len(dataset)))

    return log_path, logger, config, dataset


def read_prompts(args, log_path: str, logger):
    if os.path.exists(args.request_path):
        with open(args.request_path, "r") as f:
            prompts = []
            for l in f:
                cur = json.loads(l)
                prompts.append(cur)
        return prompts
    else:
        raise ValueError(
            f"Request file {args.request_path} does not exist. Please provide a valid request file."
        )


def run_retrieve(args):

    seed_everthing(args.seed)
    logger = init_logger_simple()
    with open(args.config_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    log_path = get_retrieve_cache_path(config)

    dataset = datasets.Dataset.load_from_disk(config["rag_config"]["data_path"])
    logger.info("Dataset columns: {}".format(dataset.column_names))
    logger.info("Dataset length: {}".format(len(dataset)))

    model_config = config["model_config"]
    tokenize_func, chat_template_func = build_tokenizer(model_config)
    all_params = {
        "tokenize_func": tokenize_func,
        "is_model_generated_retrieval": "query_generation_model_config" in config,
        **config["rag_config"],
    }
    retriver = build_retriever(**all_params)
    rag_model = RAGModel(
        logging_path=log_path,
        retrieve_context_path=log_path,
        logger=logger,
        model=None,
        retriever=retriver,
    )

    rag_model.run_context_build(build_prompt=False)


def run_model_response(args):
    log_path, logger, config, dataset = seed_and_load(args)
    init_wandb_logger(config)
    model_config = config["model_config"]
    tokenize_func, chat_template_func = build_tokenizer(model_config)
    model = build_model(
        {
            "chat_template_func": chat_template_func,
            "logging_path": log_path,
            **model_config,
        }
    )
    rag_model = RAGModel(
        logging_path=log_path,
        logger=logger,
        model=model,
        retriever=None,
    )
    prompts = read_prompts(args, log_path, logger)
    resp = rag_model.run_get_responses(prompts)
    metrics = compute_metrics_full(resp, dataset, logger)
    wandb.log(metrics)
    logger.info(f"Metrics: {metrics}")
    wandb.finish()
    return metrics


def run_metrics_compute(args):
    log_path, logger, config, dataset = seed_and_load(args)
    init_wandb_logger(config)
    with open(args.response_path, "r") as f:
        response = []
        for l in f:
            cur = json.loads(l)
            response.append(cur)

    dataset = datasets.Dataset.load_from_disk(config["rag_config"]["data_path"])
    metrics = compute_metrics_full(response, dataset, logger)
    wandb.log(metrics)
    logger.info(f"Metrics: {metrics}")
    return metrics


def run_full(args):

    log_path, logger, config, dataset = seed_and_load(args)

    if args.data_parallel > 1:
        cur_idx = list(range(args.data_parallel_rank, len(dataset), args.data_parallel))
        dataset = dataset.select(cur_idx)
        logger.info(
            f"MAIN Data parallel rank {args.data_parallel_rank} selected {len(dataset)} samples"
        )

    init_wandb_logger(config)

    model_config = config["model_config"]
    tokenize_func, chat_template_func = build_tokenizer(model_config)

    model = build_model(
        {
            "chat_template_func": chat_template_func,
            "logging_path": log_path,
            **model_config,
        }
    )
    all_params = {
        "tokenize_func": tokenize_func,
        "is_model_generated_retrieval": "query_generation_model_config" in config,
        "data_parallel": args.data_parallel,
        "data_parallel_rank": args.data_parallel_rank,
        **config["rag_config"],
    }

    retriever = build_retriever(**all_params)
    retrieve_context_path = get_retrieve_cache_path(config)
    rag_model = RAGModel(
        logging_path=log_path,
        retrieve_context_path=retrieve_context_path,
        logger=logger,
        model=model,
        retriever=retriever,
    )

    resp = rag_model.run_full()
    metrics = compute_metrics_full(resp, dataset, logger)
    wandb.log(metrics)
    logger.info(f"Metrics: {metrics}")


def main(args):
    if args.mode == "retrieve":
        run_retrieve(args)
    elif args.mode == "inference":
        run_model_response(args)
    elif args.mode == "full":
        run_full(args)
    elif args.mode == "compute_metrics":
        run_metrics_compute(args)
    else:
        raise ValueError("Invalid mode: {}".format(args.mode))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="full", type=str)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--config_path", type=str)
    parser.add_argument("--request_path", default="", type=str)
    parser.add_argument("--response_path", default="", type=str)
    parser.add_argument("--data_parallel", default=1, type=int)
    parser.add_argument("--data_parallel_rank", default=0, type=int)
    args = parser.parse_args()

    datasets.disable_caching()
    main(args)
