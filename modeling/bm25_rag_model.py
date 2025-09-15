import os
import datasets
from tqdm import tqdm
from elasticsearch import Elasticsearch
from modeling.rag_model import RetrieverBase


def build_context_batch_worker(
    data_batch: datasets.Dataset,
    rank: int,
    elasticsearch_host_name: str,
    bm25_index_name: str,
    topk: int,
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
    for i in tqdm(
        list(range(len(all_questions))),
        desc="Building context batch {}".format(rank + 1),
        position=rank + 1,
        leave=False,
    ):
        doc_list = retriever.search(
            index=bm25_index_name,
            body={
                "query": {"match": {doc_field_name: all_questions[i]}},
                "size": topk,  # specify the number of documents you want to return
            },
        )["hits"]["hits"]

        context_str_list = []
        cur_context_doc_ids = []
        for doc in doc_list:
            cur_doc = doc["_source"][doc_field_name]
            cur_doc = cur_doc.replace("<|endoftext|>", " ")
            cur_context_doc_ids.append(doc["_source"]["hash"])
            context_str_list.append(cur_doc)

        context_list.append(context_str_list)
        context_id_list.append(cur_context_doc_ids)
    data_batch["context"] = context_list
    data_batch["context_doc_ids"] = context_id_list
    return data_batch


class BM25Retriver(RetrieverBase):
    def __init__(
        self,
        topk: int,
        elasticsearch_index_name: str,
        elasticsearch_host_name: str,
        doc_field_name: str = "document",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.topk = topk
        self.elasticsearch_host_name = elasticsearch_host_name
        self.bm25_index_name = elasticsearch_index_name
        self.doc_field_name = doc_field_name

    def build_context(self, full_data: datasets.Dataset) -> datasets.Dataset:

        bs = len(full_data) // os.cpu_count()

        if bs == 0:
            bs = 1

        if len(full_data) % os.cpu_count() != 0:
            bs += 1

        dataset_with_ctx = full_data.map(
            build_context_batch_worker,
            fn_kwargs={
                "elasticsearch_host_name": self.elasticsearch_host_name,
                "bm25_index_name": self.bm25_index_name,
                "topk": self.topk,
                "doc_field_name": self.doc_field_name,
            },
            with_rank=True,
            batched=True,
            batch_size=bs,
            num_proc=os.cpu_count(),
        )

        return dataset_with_ctx
