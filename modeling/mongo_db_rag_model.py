import os
import json
import random
import datasets
from tqdm import tqdm
from pymongo import MongoClient
from datetime import datetime, timedelta
from modeling.rag_model import RetrieverBase
from utils.utils import conversation_pretty_print_v2, summary_with_meta_data, time_decode


DB_NAME = "wildchat-aqa-db"
COLLECTION_NAME = "wildchat"

def get_context_query(condition_type, condition_value):
    query = {}

    if (
        len(condition_type) > 1
        and len(set(condition_type)) == 1
        and condition_type[0] in {"label_level_1", "label_level_2"}
    ):
        real_query = {"$match": {"labels": {"$all": condition_value}}}
    else:
        for i in range(len(condition_type)):
            cur_cond = condition_type[i]
            cur_value = condition_value[i]

            if cur_cond == "country":
                query["country"] = [cur_value]
            elif cur_cond == "language":
                query["language"] = [cur_value]
            elif cur_cond in {"label_level_1", "label_level_2"}:
                if "labels" not in query:
                    query["labels"] = [cur_value]
                else:
                    query["labels"].append(cur_value)
            elif cur_cond == "user_name":

                if "user_name" not in query:
                    query["user_name"] = [cur_value]
                else:
                    query["user_name"].append(cur_value)
            elif cur_cond == "time_week":
                st = datetime.strptime(cur_value, "%Y-%m-%d %H:%M:%S")
                query["timestamp"] = {
                    "$gte": st,
                    "$lt": st + timedelta(days=7),
                }
            elif cur_cond == "keywords":
                if "keywords" not in query:
                    query["keywords.value"] = [cur_value]
                else:
                    query["keywords.value"].append(cur_value)
            elif cur_cond == "keywords_aggregated":
                if "keywords_aggregated" not in query:
                    query["keywords_aggregated.value"] = [cur_value]
                else:
                    query["keywords_aggregated.value"].append(cur_value)

        if len(condition_type) > 0:

            conds = []

            for k, v in query.items():
                if k == "timestamp":
                    conds.append({k: v})
                else:
                    conds.append({k: {"$in": v}})

            real_query = {"$match": {"$and": conds}}
        else:
            real_query = {"$match": {}}
    return real_query


def mongo_db_build_context_worker(
    data_batch: datasets.Dataset,
    rank: int,
    mongodb_host_name: str,
    doc_field_name: str,
    topk: int,
):

    retriever = MongoClient(mongodb_host_name)
    all_conditions = data_batch["condition_type"]
    all_values = data_batch["condition_value"]
    all_contexts = []
    context_id_list = []
    for i in tqdm(
        list(range(len(all_conditions))),
        desc="Building context batch {}".format(rank + 1),
        position=rank + 1,
        leave=False,
    ):
        condition_type = all_conditions[i]
        condition_value = all_values[i]
        # create mongodb query based on condition type and value

        real_query = get_context_query(condition_type, condition_value)

        # query mongodb
        db = retriever[DB_NAME]
        collection = db[COLLECTION_NAME]
        db_result = collection.aggregate([real_query])
        result = []

        for item in db_result:
            result.append(
                {
                    "conversation": item["conversation"],
                    "summary": item["summary"],
                    "user_name": item["user_name"],
                    "country": item["country"],
                    "timestamp": time_decode(item["timestamp"]),
                    "hash": item["hash"],
                }
            )

        random.shuffle(result)
        context_str_list = []
        cur_doc_id_list = []

        for idx, item in enumerate(result[:topk]):
            if doc_field_name == "document":
                res = conversation_pretty_print_v2(
                    json.loads(item["conversation"]),
                    item["user_name"],
                    item["country"],
                    item["timestamp"],
                )
            elif doc_field_name == "document_summary":
                res = summary_with_meta_data(
                    item["summary"],
                    item["user_name"],
                    item["country"],
                    item["timestamp"],
                )
            else:
                raise ValueError("Invalid doc_field_name")

            res = res.replace("<|endoftext|>", " ")
            cur_doc_id_list.append(item["hash"])
            context_str_list.append(res)

        all_contexts.append(context_str_list)
        context_id_list.append(cur_doc_id_list)

    data_batch["context"] = all_contexts
    data_batch["context_doc_ids"] = context_id_list
    return data_batch


class MongoDBRetriever(RetrieverBase):
    def __init__(
        self,
        mongodb_host_name: str,
        topk: int = 1048576,
        doc_field_name: str = "document",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.mongodb_host_name = mongodb_host_name
        self.doc_field_name = doc_field_name
        self.topk = topk

    def build_context(self, full_data: datasets.Dataset):
        bs = len(full_data) // os.cpu_count()

        if bs == 0:
            bs = 1

        if len(full_data) % os.cpu_count() != 0:
            bs += 1

        dataset_with_ctx = full_data.map(
            mongo_db_build_context_worker,
            fn_kwargs={
                "mongodb_host_name": self.mongodb_host_name,
                "doc_field_name": self.doc_field_name,
                "topk": self.topk,
            },
            batched=True,
            with_rank=True,
            batch_size=bs,
            desc="Building context",
            num_proc=os.cpu_count(),
        )

        return dataset_with_ctx
