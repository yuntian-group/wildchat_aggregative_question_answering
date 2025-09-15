import os
import glob
import yaml
import json
import wandb
import torch
import random
import numpy as np
import transformers
from tqdm import tqdm
from transformers import (
    TrainerCallback,
    TrainerState,
    TrainerControl,
    TrainingArguments,
    EvalPrediction,
    PreTrainedTokenizer,
)
from typing import List, Dict
from rouge_score import rouge_scorer
from datetime import datetime, timedelta

ART_WORK_SET = {
    "Video Games",
    "Tabletop Games",
    "Manga/Anime",
    "Film",
    "TV Show",
    "Western Cartoon/Comic",
    "Musical",
}

BOOK_SET = {"Book"}
PROGRAMMING_LANGUAGE_SET = {"Programming Language"}

PUBLIC_FIGURE_SET = {"Public Figure"}

AVG_TOKEN_PER_CONVERSATION = 1000
AVG_TOKEN_PER_CONVERSATION_SUMMARY = 30
TOPK_PRED = 10


def seed_everthing(seed: int):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    transformers.set_seed(seed)



def summary_with_meta_data(summary, user_name, country, date, lower=False):
    conversation_str = "User: {}\nCountry: {}\nDate: {}\n\n".format(
        user_name, country, date
    )
    conversation_str += summary if not lower else summary.lower()
    return conversation_str


def converstation_pretty_print(
    conv: List[Dict[str, str]], user_name: str = None, conv_id: str = None
) -> str:
    if conv_id is not None:
        conversation_str = f"ID: {conv_id}\n"
    else:
        conversation_str = ""
    for i, turn in enumerate(conv):
        if i % 2 == 0:
            if user_name is not None:
                conversation_str += "{}: {}\n----\n".format(user_name, turn["content"])
            else:
                conversation_str += "<User Request>: {}\n----\n".format(turn["content"])
        else:
            conversation_str += "<Agent Response>: {}\n----\n".format(turn["content"])
    return conversation_str


def conversation_pretty_print_list(
    conv: List[Dict[str, str]], user_name: str = None, conv_id: str = None
):
    conversation_str = []
    if conv_id is not None:
        conversation_str.append(f"ID: {conv_id}")
    for i, turn in enumerate(conv):
        if i % 2 == 0:
            if user_name is not None:
                conversation_str.append(f"{user_name}: {turn['content']}")
            else:
                conversation_str.append(f"<User Request>: {turn['content']}")
        else:
            conversation_str.append(f"<Agent Response>: {turn['content']}")
    return conversation_str


def conversation_pretty_print_v2(
    conv: List[Dict[str, str]],
    user_name: str,
    country: str,
    date: str,
    use_header: bool = True,
    lower: bool = False,
) -> str:

    if use_header:
        conversation_str = "User: {}\nCountry: {}\nDate: {}\n\n".format(
            user_name, country, date
        )
    else:
        conversation_str = ""
    for i, turn in enumerate(conv):
        if i % 2 == 0:
            conversation_str += "< {} >: {}\n".format(
                user_name, turn["content"] if not lower else turn["content"].lower()
            )
        else:
            conversation_str += "< response >: {}\n".format(
                turn["content"] if not lower else turn["content"].lower()
            )
    return conversation_str


def conversation_pretty_print_v2_list(
    conv: List[Dict[str, str]],
    user_name: str,
    lower: bool = False,
):
    conversation_list = []
    for i, turn in enumerate(conv):
        if i % 2 == 0:
            conversation_list.append(
                "< {} >: {}\n".format(
                    user_name, turn["content"] if not lower else turn["content"].lower()
                )
            )
        else:
            conversation_list.append(
                "< response >: {}\n".format(
                    turn["content"] if not lower else turn["content"].lower()
                )
            )
    return conversation_list


def keywords_type_to_name(keywords_type: str) -> str:
    if keywords_type in ART_WORK_SET:
        return "creative work such as games, tv shows, movies, cartoon, or anime"
    elif keywords_type in BOOK_SET:
        return "books, literature, or novels"
    elif keywords_type in PROGRAMMING_LANGUAGE_SET:
        return "programming languages"
    elif keywords_type in PUBLIC_FIGURE_SET:
        return "public figures, celebrities, and influencers"
    else:
        raise ValueError("Unknown keywords type: {}".format(keywords_type))


def condition_pretty_print(
    condition_types: List[str],
    condition_values: List[str],
    target_type: str,
    target_options: List[str],
    taxonomies,
    most_popular_keywords_type: str = "",
    use_target_options: bool = True,
):
    """
    Pretty print the condition types and values.
    """
    condition_str = "Conditions: \n"
    target_str = ""

    target_type_to_target_str = {
        "label_level_1": "Popular Topics",
        "label_level_2": "Popular Subtopics under Topics",
        "time_week": "Most active time in unit of week",
        "user_name": "Most active users",
        "user_name_grouped": "Most active user groups",
        "country": "Most popular country user come from",
        "language": "Most popular language user use",
        "keywords_aggregated": "Most widely refered or used {}",
        "keywords_aggregated_grouped": "Most widely refered or used {}",
    }

    grouped = False
    common_interest_flag = False
    joint_topic_flag = False

    if len(target_options[0].split(",")) > 1:
        grouped = True

    if len(set(condition_types)) == 1 and len(condition_types) > 1:
        if condition_types[0] == "user_name":
            condition_str += (
                "common user names of user_name: " + ", ".join(condition_values) + "\n"
            )
            common_interest_flag = True
        elif condition_types[0] in {"label_level_1", "label_level_2"}:
            condition_str += "involve multiple topics in the same conversations: \n"
            for i in range(len(condition_values)):
                condition_str += "{}: {}\n".format(
                    condition_types[i],
                    taxonomies[condition_values[i]]["class_name"].lower()
                    + ": "
                    + taxonomies[condition_values[i]]["class_description"],
                )
            joint_topic_flag = True
        else:
            raise ValueError()
    elif len(condition_types) == 0:
        condition_str += "No condition\n\n"
    else:

        for i in range(len(condition_types)):
            if condition_types[i] == "label_level_1":
                condition_str += "{}:\n {}\n".format(
                    condition_types[i],
                    taxonomies[condition_values[i]]["class_name"].lower()
                    + ": "
                    + taxonomies[condition_values[i]]["class_description"],
                )
            elif condition_types[i] == "label_level_2":

                cur_class = condition_values[i]
                cur_str = (
                    taxonomies[condition_values[i]]["class_name"].lower()
                    + ": "
                    + taxonomies[cur_class]["class_description"]
                )

                condition_str += "{}:\n {}\n".format(condition_types[i], cur_str + "\n")
            elif condition_types[i] == "time_week":
                date_string = condition_values[i]
                date_obj = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
                # remove h
                date_str_start = date_obj.strftime("%Y-%m-%d")
                date_str_end = (date_obj + timedelta(days=6)).strftime("%Y-%m-%d")
                condition_str += "{}: {} - {}\n".format(
                    condition_types[i], date_str_start, date_str_end
                )
            else:
                condition_str += "{}: {}\n".format(
                    condition_types[i], condition_values[i]
                )

        condition_str += "\n"

    if grouped:
        target_type += "_grouped"

    if common_interest_flag and target_type in {"label_level_1", "label_level_2"}:
        if target_type == "label_level_1":
            target_type_description = "Common user interest topic"
        elif target_type == "label_level_2":
            target_type_description = "Common user interest subtopic"
    else:
        target_type_description = target_type_to_target_str[target_type]

    if target_type in {"keywords_aggregated", "keywords_aggregated_grouped"}:
        target_type_description = target_type_description.format(
            keywords_type_to_name(most_popular_keywords_type)
        )

    target_str += "Target Type: {}".format(target_type_description) + "\n\n"

    if use_target_options:
        target_str += "Target Options:\n"
        for i in range(len(target_options)):
            if target_type == "label_level_1":
                target_str += "{}: {}\n".format(
                    i, taxonomies[target_options[i]]["class_name"]
                )
            elif target_type == "label_level_2":
                cur_class = target_options[i]
                cur_class_name = taxonomies[cur_class]["class_name"]
                # cur_class_description = taxonomies[cur_class]["class_description"]

                target_str += "{}. {}\n".format(i, cur_class_name) + "\n"
            elif target_type == "time_week":
                date_string = target_options[i]
                date_obj = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
                # remove h
                date_str_start = date_obj.strftime("%Y-%m-%d")
                date_str_end = (date_obj + timedelta(days=6)).strftime("%Y-%m-%d")
                target_str += "{}. {} - {}\n".format(i, date_str_start, date_str_end)
            else:
                target_str += "{}. {}\n".format(i, target_options[i])

    return condition_str + target_str


def parse_response_single(resp, hash):
    if resp is None:
        return []
    cur_res = resp.split("</think>")
    if len(cur_res) > 1:
        resp = cur_res[1].strip()
    else:
        resp = cur_res[0].strip()

    resp1 = resp.replace("```json", "", -1)
    resp2 = resp1.replace("```", "", -1)
    st = resp2.find("{")
    ed = resp2.rfind("}")

    if st == -1 or ed == -1:
        st = resp2.find('"answer":')
        ed = len(resp2) - 1
    try:
        try:
            ans_parsed = json.loads(resp2[st : ed + 1])
            cur_prediction = [int(x) for x in ans_parsed["answer"]]
            if len(cur_prediction) > TOPK_PRED:
                cur_prediction = cur_prediction[:TOPK_PRED]
        except:
            json_ret = resp2[st : ed + 1]
            arr_st = json_ret.find("[")
            arr_ed = json_ret.rfind("]")
            arr_resp = json_ret[arr_st : arr_ed + 1]
            arr = json.loads(arr_resp)
            cur_prediction = [int(x) for x in arr]
            if len(cur_prediction) > TOPK_PRED:
                cur_prediction = cur_prediction[:TOPK_PRED]
    except:
        cur_prediction = []
        print("Error", hash)
    return cur_prediction


def load_all_taxonomy(config_path):
    with open(config_path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    level_1_taxonomy_path = config["level_1_taxonomy_path"]
    level_2_taxonomy_paths = config["level_2_taxonomy_path"]

    taxonomies = {}

    with open(os.path.join(level_1_taxonomy_path)) as f:
        level_1_classes = json.load(f)["classes"]
        for item in level_1_classes:
            taxonomies[str(item["index"])] = item

    level_2_count = 0

    for k, level_2_taxonomy_path in level_2_taxonomy_paths.items():
        with open(os.path.join(level_2_taxonomy_path)) as f:
            level_2_classes = json.load(f)["classes"]
            level_2_count += len(level_2_classes)
            for item in level_2_classes:
                taxonomies[str(k) + "." + str(item["index"])] = item
    return taxonomies


def time_decode(x):
    return datetime.strftime(x, "%B %d, %Y %H:%M:%S")


def parse_embedding_output(path: str):
    hash_to_embedding = {}
    for idx, p in enumerate(
        tqdm(glob.glob(os.path.join(path, "batch_output*")), desc="Parsing")
    ):
        print("Parsing file: {}".format(p))
        for line in open(p):
            try:
                data = json.loads(line)
                embedding = np.array(
                    data["response"]["body"]["data"][0]["embedding"], dtype=np.float16
                )
                unique_id = data["custom_id"]
                hash_to_embedding[unique_id] = embedding
            except Exception as e:
                print("Error: {}: {}".format(e, unique_id))
    return hash_to_embedding