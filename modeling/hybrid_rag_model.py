import os
import datasets
from elasticsearch import Elasticsearch
from modeling.rag_model import RetrieverBase


class HybridRetriever(RetrieverBase):
    def __init__(
        self,
        topk: int,
        elasticsearch_index_name: str,
        elasticsearch_host_name: str,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.topk = topk
        self.bm25_index_name = elasticsearch_index_name
        self.elasticsearch_host_name = elasticsearch_host_name

    def build_context(self, full_data: datasets.Dataset) -> str:
        def build_context_batch_worker(
            data_batch: datasets.Dataset,
            max_context_token_count: int,
            tokenize_func: callable,
        ):
            retriever = Elasticsearch(
                "http://elastic:{}".format(os.environ["ELASTIC_PASSWORD"])
                + "@{}".format(self.elasticsearch_host_name),
                verify_certs=False,
                ssl_show_warn=False,
            )

            context_list = []
            for data_sample in data_batch:
                doc_list = retriever.search(
                    query={"match": {"document": data_sample["question"]}},
                    knn={
                        "field": "embedding",
                        "query_vector": data_sample["question_embedding"],
                        "num_candidates": 5 * self.topk,
                        "k": self.topk,
                    },
                    size=self.topk,
                )["hits"]["hits"]

                context_str = ""
                token_count = 0

                for doc in doc_list:
                    cur_doc = doc["_source"]["document"]

                    cur_doc = cur_doc.replace("<|endoftext|>", " ")

                    cur_token_count = len(tokenize_func(cur_doc))

                    if token_count + cur_token_count < max_context_token_count:
                        token_count += cur_token_count
                        context_str += cur_doc
                        context_str += "\n\n"
                    else:
                        break
                context_list.append(context_str)
            data_batch["context"] = context_list
            return data_batch

        bs = len(full_data) // os.cpu_count()

        if bs == 0:
            bs = 1

        if len(full_data) % os.cpu_count() != 0:
            bs += 1

        dataset_with_ctx = full_data.map(
            build_context_batch_worker,
            fn_kwargs={
                "max_context_token_count": self.max_context_token_count,
                "tokenize_func": self.tokenize_func,
            },
            batched=True,
            batch_size=bs,
            num_proc=os.cpu_count(),
        )

        return dataset_with_ctx
