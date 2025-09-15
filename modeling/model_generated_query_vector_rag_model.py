import os
import json
import datasets
from tqdm import tqdm
from typing import List
from datetime import datetime
from elasticsearch import Elasticsearch
from modeling.model_generated_query_rag_model import (
    ModelGeneratedQueryRAGRetriever,
    build_filter,
    MAX_QUERY,
)


def build_single_elasticsearch_dense_request_list(
    x: str,
    embeddings: List[List[float]],
    embedding_flag: List[int],
    question_embedding: List[float],
    emebdding_field_name: str,
    topk: int,
    force_question_embedding: bool = False,
):
    try:
        generated_request = json.loads(x)["query"]
    except:
        print(f"Error parsing JSON: {x}")
        return [{"query": {"bool": {}}}]

    all_filters = build_filter(generated_request)
    bool_value = {}

    if len(all_filters) > 0:
        bool_value["filter"] = all_filters

    generated_query = generated_request.get("queries", [])[:MAX_QUERY]

    all_queries = []

    for idx, q in enumerate(generated_query):
        if embedding_flag[idx] != 0 and not force_question_embedding:
            knn_part = {
                "knn": {
                    "field": emebdding_field_name,
                    "query_vector": embeddings[idx],
                    "num_candidates": 5 * topk,
                    "k": topk,
                }
            }

        else:
            knn_part = {
                "knn": {
                    "field": emebdding_field_name,
                    "query_vector": question_embedding,
                    "num_candidates": 5 * topk,
                    "k": topk,
                }
            }

        cur_bool_value = bool_value.copy()
        cur_bool_value["should"] = [knn_part]
        all_queries.append({"query": {"bool": cur_bool_value}})

    if len(all_queries) == 0:
        all_queries.append({"query": {"bool": bool_value}})

    return all_queries


def build_context_batch_worker(
    data_batch: datasets.Dataset,
    rank: int,
    elasticsearch_host_name: str,
    bm25_index_name: str,
    topk: int,
    doc_field_name: str,
    force_question_embedding: bool = False,
):
    retriever = Elasticsearch(
        "http://elastic:{}".format(os.environ["ELASTIC_PASSWORD"])
        + "@{}".format(elasticsearch_host_name),
        verify_certs=False,
        ssl_show_warn=False,
    )

    all_generated_requests = data_batch["generated_query"]
    # all_questions = data_batch["question"]
    context_list = []
    context_id_list = []
    all_question_embeddings = data_batch["question_embedding"]
    all_embedding_flag = data_batch["query_embedding_success_flag"]
    all_generated_query_embedding = data_batch["query_embeddings"]

    if doc_field_name == "document":
        embeddding_name = "embedding"
    elif doc_field_name == "document_summary":
        embeddding_name = "summary_embedding"
    else:
        raise ValueError("doc_field_name should be either document or summary")

    for i in tqdm(
        list(range(len(all_generated_requests))),
        desc="Retrieving documents part {}".format(rank),
        position=rank,
        leave=False,
    ):
        generated_request_raw = all_generated_requests[i]
        generated_request_list = build_single_elasticsearch_dense_request_list(
            generated_request_raw,
            all_generated_query_embedding[i],
            all_embedding_flag[i],
            all_question_embeddings[i],
            embeddding_name,
            topk,
            force_question_embedding=force_question_embedding,
        )

        hash_to_score = {}
        hash_to_doc = {}

        for generated_request in generated_request_list:
            generated_request["size"] = int(topk // len(generated_request_list) * 2)
            doc_list = retriever.search(index=bm25_index_name, body=generated_request)[
                "hits"
            ]["hits"]

            doc_list = retriever.search(index=bm25_index_name, body=generated_request)[
                "hits"
            ]["hits"]

            for doc in doc_list:
                doc_hash = doc["_source"]["hash"]
                if doc_hash not in hash_to_score:
                    hash_to_score[doc_hash] = 0
                    hash_to_doc[doc_hash] = doc

                score = doc["_score"]
                hash_to_score[doc_hash] += score
                if score > hash_to_doc[doc_hash]["_score"]:
                    hash_to_doc[doc_hash] = doc

        doc_list = list(hash_to_doc.values())
        doc_list.sort(key=lambda x: hash_to_score[x["_source"]["hash"]], reverse=True)
        doc_list = doc_list[:topk]

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


class ModelGeneratedQueryVectorRAGRetriever(ModelGeneratedQueryRAGRetriever):
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

        if self.force_no_query:
            raise ValueError("force_question_query cannot be both True")

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
                "force_question_embedding": self.force_question_query,
            },
            with_rank=True,
            batched=True,
            batch_size=bs,
            num_proc=os.cpu_count(),
        )

        return dataset_with_ctx
