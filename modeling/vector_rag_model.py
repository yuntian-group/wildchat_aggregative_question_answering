import os
import datasets
from tqdm import tqdm
from elasticsearch import Elasticsearch
from modeling.rag_model import RetrieverBase


def build_context_batch_worker(
    data_batch: datasets.Dataset,
    rank: int,
    bm25_index_name: str,
    topk: int,
    elasticsearch_host_name: str,
    doc_field_name: str,
):
    retriever = Elasticsearch(
        "http://elastic:{}".format(os.environ["ELASTIC_PASSWORD"])
        + "@{}".format(elasticsearch_host_name),
        verify_certs=False,
        ssl_show_warn=False,
    )

    context_list = []
    context_id_list = []
    all_questions = data_batch["question"]
    all_embeddings = data_batch["question_embedding"]
    if doc_field_name == "document":
        embeddding_name = "embedding"
    elif doc_field_name == "document_summary":
        embeddding_name = "summary_embedding"
    else:
        raise ValueError("doc_field_name should be either document or summary")
    for i in tqdm(
        list(range(len(all_questions))),
        desc="Building context batch {}".format(rank + 1),
        position=rank + 1,
        leave=False,
    ):
        doc_list = retriever.search(
            index=bm25_index_name,
            knn={
                "field": embeddding_name,
                "query_vector": all_embeddings[i],
                "num_candidates": topk,
                "k": topk,
            },
            size=topk,
        )["hits"]["hits"]

        cur_context_str_list = []
        cur_doc_id_list = []

        for doc in doc_list:
            cur_doc = doc["_source"][doc_field_name]
            cur_doc = cur_doc.replace("<|endoftext|>", " ")
            cur_doc_id_list.append(doc["_id"])
            cur_context_str_list.append(cur_doc)

        context_list.append(cur_context_str_list)
        context_id_list.append(cur_doc_id_list)
    data_batch["context"] = context_list
    data_batch["context_doc_ids"] = context_id_list
    return data_batch


class VectorDenseRetriever(RetrieverBase):
    def __init__(
        self,
        topk: int,
        elasticsearch_index_name: str,
        elasticsearch_host_name: str,
        doc_field_name: str = "document",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.topk = topk
        self.bm25_index_name = elasticsearch_index_name
        self.elasticsearch_host_name = elasticsearch_host_name
        self.doc_field_name = doc_field_name

    def build_context(self, full_data) -> str:

        bs = len(full_data) // os.cpu_count()

        if bs == 0:
            bs = 1

        if len(full_data) % os.cpu_count() != 0:
            bs += 1

        dataset_with_ctx = full_data.map(
            build_context_batch_worker,
            fn_kwargs={
                "elasticsearch_host_name": self.elasticsearch_host_name,
                "topk": self.topk,
                "bm25_index_name": self.bm25_index_name,
                "doc_field_name": self.doc_field_name,
            },
            batched=True,
            with_rank=True,
            batch_size=bs,
            num_proc=os.cpu_count(),
        )

        return dataset_with_ctx
