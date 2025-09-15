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


def build_single_elasticsearch_hybrid_request_list(
    x: str,
    embeddings: List[List[float]],
    embedding_flag: List[int],
    question_embedding: List[float],
    emebdding_field_name: str,
    topk: int,
):
    try:
        generated_request = json.loads(x)["query"]
    except:
        print(f"Error parsing JSON: {x}")
        return [({"query": {"bool": {}}}, {"query": {"bool": {}}})]

    all_filters = build_filter(generated_request)
    # print(generated_request, all_filters)
    bool_value = {}

    if len(all_filters) > 0:
        bool_value["filter"] = all_filters

    generated_query = generated_request.get("queries", [])[:MAX_QUERY]

    all_queries = []

    for idx, q in enumerate(generated_query):
        if embedding_flag[idx] != 0:
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

        bm25_part = {"match": {"document": q}}
        cur_bool_knn_value = bool_value.copy()
        cur_bool_knn_value["should"] = [knn_part]
        cur_bool_bm25_value = bool_value.copy()
        cur_bool_bm25_value["should"] = [bm25_part]
        knn_full = {"query": {"bool": cur_bool_knn_value}}
        bm25_full = {"query": {"bool": cur_bool_bm25_value}}
        all_queries.append((bm25_full, knn_full))

    if len(all_queries) == 0:
        all_queries.append(
            ({"query": {"bool": bool_value}}, {"query": {"bool": bool_value}})
        )

    return all_queries


def build_context_batch_worker(
    data_batch: datasets.Dataset,
    rank: int,
    elasticsearch_host_name: str,
    bm25_index_name: str,
    topk: int,
    doc_field_name: str,
    alpha: float = 0.5,
    beta: float = 0.5,
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
        generated_request_list = build_single_elasticsearch_hybrid_request_list(
            generated_request_raw,
            all_generated_query_embedding[i],
            all_embedding_flag[i],
            all_question_embeddings[i],
            embeddding_name,
            topk,
        )

        hash_to_score = {}
        hash_to_doc = {}

        for generated_request in generated_request_list:

            bm25_query_body, knn_query_body = generated_request

            # Combine the two queries into a single query
            knn_res = retriever.search(index=bm25_index_name, body=knn_query_body)[
                "hits"
            ]["hits"]

            # Then, search using BM25
            bm25_res = retriever.search(index=bm25_index_name, body=bm25_query_body)[
                "hits"
            ]["hits"]
            knn_rank_index_score = {}
            cur_max_score = {}
            cur_hash_to_doc = {}

            for idx, doc in enumerate(knn_res):
                cur_knn_score = 1.0 / (idx + 1)
                if doc["_source"]["hash"] not in cur_max_score:
                    cur_max_score[doc["_source"]["hash"]] = cur_knn_score
                    cur_hash_to_doc[doc["_source"]["hash"]] = doc
                else:
                    if cur_knn_score > cur_max_score[doc["_source"]["hash"]]:
                        cur_max_score[doc["_source"]["hash"]] = cur_knn_score
                        cur_hash_to_doc[doc["_source"]["hash"]] = doc

                if doc["_source"]["hash"] not in knn_rank_index_score:
                    knn_rank_index_score[doc["_source"]["hash"]] = cur_knn_score
                else:
                    knn_rank_index_score[doc["_source"]["hash"]] += cur_knn_score

            bm25_rank_index_score = {}
            for idx, doc in enumerate(bm25_res):
                cur_bm25_score = 1.0 / (idx + 1)
                if doc["_source"]["hash"] not in cur_max_score:
                    cur_max_score[doc["_source"]["hash"]] = cur_bm25_score
                    cur_hash_to_doc[doc["_source"]["hash"]] = doc
                else:
                    if cur_bm25_score > cur_max_score[doc["_source"]["hash"]]:
                        cur_max_score[doc["_source"]["hash"]] = cur_bm25_score
                        cur_hash_to_doc[doc["_source"]["hash"]] = doc

                if doc["_source"]["hash"] not in bm25_rank_index_score:
                    bm25_rank_index_score[doc["_source"]["hash"]] = cur_bm25_score
                else:
                    bm25_rank_index_score[doc["_source"]["hash"]] += cur_bm25_score

            rrf_score = {}

            all_keys = set(
                list(knn_rank_index_score.keys()) + list(bm25_rank_index_score.keys())
            )

            for k in all_keys:
                if k in knn_rank_index_score and k in bm25_rank_index_score:
                    rrf_score[k] = (
                        knn_rank_index_score[k] * alpha
                        + bm25_rank_index_score[k] * beta
                    ) / 2
                elif k in knn_rank_index_score:
                    rrf_score[k] = knn_rank_index_score[k] * alpha
                elif k in bm25_rank_index_score:
                    rrf_score[k] = bm25_rank_index_score[k] * beta
                else:
                    rrf_score[k] = 0
            # sort the results based on the RRF score
            rrf_score = sorted(rrf_score.items(), key=lambda x: x[1], reverse=True)

            for doc_hash, score in rrf_score:
                doc = cur_hash_to_doc[doc_hash]
                doc["_score"] = score

                if doc_hash not in hash_to_doc:
                    hash_to_doc[doc_hash] = doc
                    hash_to_score[doc_hash] = score
                else:
                    if score > hash_to_score[doc_hash]:
                        hash_to_doc[doc_hash] = doc
                    hash_to_score[doc_hash] += score

        doc_list = list(hash_to_doc.values())
        doc_list.sort(key=lambda x: hash_to_score[x["_source"]["hash"]], reverse=True)
        doc_list = doc_list[:topk]

        cur_context_doc_ids = []
        cur_context_str_list = []
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


class ModelGeneratedQueryHybridRAGRetriever(ModelGeneratedQueryRAGRetriever):
    def __init__(
        self,
        topk: int,
        elasticsearch_index_name: str,
        elasticsearch_host_name: str,
        doc_field_name: str = "document",
        knn_weight: float = 0.3,
        bm25_weight: float = 0.7,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.topk = topk
        self.elasticsearch_index_name = elasticsearch_index_name
        self.elasticsearch_host_name = elasticsearch_host_name
        self.doc_field_name = doc_field_name
        self.knn_weight = knn_weight
        self.bm25_weight = bm25_weight

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
                "alpha": self.knn_weight,
                "beta": self.bm25_weight,
            },
            with_rank=True,
            batched=True,
            batch_size=bs,
            num_proc=os.cpu_count(),
        )

        return dataset_with_ctx
