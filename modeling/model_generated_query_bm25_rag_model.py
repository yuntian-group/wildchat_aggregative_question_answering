import os
import json
import datasets
from tqdm import tqdm
from datetime import datetime
from elasticsearch import Elasticsearch
from modeling.model_generated_query_rag_model import (
    ModelGeneratedQueryRAGRetriever,
    build_filter,
    MAX_QUERY,
)


def build_single_elasticsearch_request(
    x, question: str, force_question_query: bool = False, force_no_query: bool = False
):
    try:
        generated_request = json.loads(x)["query"]
    except:
        print(f"Error parsing JSON: {x}")
        return {"query": {"bool": {}}}

    all_filters = build_filter(generated_request)

    bool_value = {}

    if len(all_filters) > 0:
        bool_value["filter"] = all_filters

    if force_question_query:
        generated_query = [question]
    elif force_no_query:
        generated_query = []
    else:
        generated_query = generated_request.get("queries", [])[:MAX_QUERY]
    # generated_query = []

    queries_match = []
    if len(generated_query) > 0:
        for q in generated_query:
            queries_match.append({"match": {"document": q}})
    if len(queries_match) > 0:
        bool_value["should"] = queries_match
        # bool_value["minimum_should_match"] = 0

    query = {
        "query": {
            "bool": bool_value,
        }
    }
    return query


def build_context_batch_worker(
    data_batch: datasets.Dataset,
    rank: int,
    elasticsearch_host_name: str,
    bm25_index_name: str,
    topk: int,
    doc_field_name: str,
    force_question_query: bool = False,
    force_no_query: bool = False,
):
    retriever = Elasticsearch(
        "http://elastic:{}".format(os.environ["ELASTIC_PASSWORD"])
        + "@{}".format(elasticsearch_host_name),
        verify_certs=False,
        ssl_show_warn=False,
    )

    all_generated_requests = data_batch["generated_query"]
    all_questions = data_batch["question"]
    context_list = []
    context_id_list = []

    for i in tqdm(
        list(range(len(all_generated_requests))),
        desc="Retrieving documents part {}".format(rank),
        position=rank,
        leave=False,
    ):
        generated_request = all_generated_requests[i]
        cur_question = all_questions[i]
        generated_request = build_single_elasticsearch_request(
            generated_request, cur_question, force_question_query, force_no_query
        )
        doc_list = retriever.search(
            index=bm25_index_name,
            body=generated_request,
            size=topk,
        )["hits"]["hits"]

        cur_context_str_list = []
        cur_context_doc_ids = []
        for doc in doc_list:
            cur_doc = doc["_source"][doc_field_name]
            cur_doc = cur_doc.replace("<|endoftext|>", " ")
            cur_context_str_list.append(cur_doc)
            cur_context_doc_ids.append(doc["_source"]["hash"])

        context_list.append(cur_context_str_list)
        context_id_list.append(cur_context_doc_ids)

    data_batch["context"] = context_list
    data_batch["context_doc_ids"] = context_id_list
    return data_batch


class ModelGeneratedQueryBM25RAGRetriever(ModelGeneratedQueryRAGRetriever):
    def __init__(
        self,
        topk: int,
        elasticsearch_index_name: str,
        elasticsearch_host_name: str,
        doc_field_name: str = "document",
        force_question_query: bool = False,
        force_no_query: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.topk = topk
        self.elasticsearch_index_name = elasticsearch_index_name
        self.elasticsearch_host_name = elasticsearch_host_name
        self.doc_field_name = doc_field_name
        self.force_question_query = force_question_query
        self.force_no_query = force_no_query

        if self.force_question_query and self.force_no_query:
            raise ValueError(
                "force_question_query and force_no_query cannot be both True"
            )

    def build_context(self, full_data: datasets.Dataset) -> str:

        bs = len(full_data) // os.cpu_count()

        if bs == 0:
            bs = 1

        if len(full_data) % os.cpu_count() != 0:
            bs += 1

        dataset_with_ctx = full_data.map(
            build_context_batch_worker,
            fn_kwargs={
                "elasticsearch_host_name": self.elasticsearch_host_name,
                "bm25_index_name": self.elasticsearch_index_name,
                "topk": self.topk,
                "doc_field_name": self.doc_field_name,
                "force_question_query": self.force_question_query,
                "force_no_query": self.force_no_query,
            },
            with_rank=True,
            batched=True,
            batch_size=bs,
            num_proc=os.cpu_count(),
        )

        return dataset_with_ctx
