import os
import argparse
import datasets
import numpy as np
import elasticsearch
from tqdm import tqdm
from elasticsearch import helpers


def es_index_worker(data_batch, rank, index_name, embedding_dim):
    client = elasticsearch.Elasticsearch(
        "http://elastic:{}".format(os.environ["ELASTIC_PASSWORD"]) + "@localhost:9200",
        verify_certs=False,
        ssl_show_warn=False,
        request_timeout=30,
    )

    all_documents = data_batch["document"]
    all_hashes = data_batch["hash"]
    all_unique_ids = data_batch["unique_id"]
    all_embeddings = data_batch["embedding"]
    all_timestamps = data_batch["timestamp"]
    all_user_names = data_batch["user_name"]
    all_countries = data_batch["country"]

    actions = (
        {
            "_index": index_name,
            "_id": all_hashes[idx],
            "_source": {
                "document": all_documents[idx],
                "hash": all_hashes[idx],
                "unique_id": all_unique_ids[idx],
                "embedding": all_embeddings[idx],
                "timestamp": all_timestamps[idx].isoformat(),
                "user_name": all_user_names[idx],
                "country": all_countries[idx],
            },
        }
        for idx in range(len(all_hashes))
    )

    successes = 0
    for ok, item in tqdm(
        helpers.parallel_bulk(
            client, actions, chunk_size=10000, thread_count=16, queue_size=16
        ),
        desc="Indexing batch {}".format(rank),
        position=rank,
        leave=False,
    ):
        if ok:
            successes += 1
    print("Indexed batches:", successes)


def main(args):
    documents = datasets.Dataset.load_from_disk(args.data_path)
    print("Total documents:", len(documents))

    client = elasticsearch.Elasticsearch(
        "http://elastic:{}".format(os.environ["ELASTIC_PASSWORD"]) + "@localhost:9200",
        verify_certs=False,
        ssl_show_warn=False,
        request_timeout=30,
    )
    client.ping()
    if client.indices.exists(index="wildchat_aqa_document"):
        client.indices.delete(index="wildchat_aqa_document")
    if client.indices.exists(index="wildchat_aqa_summary"):
        client.indices.delete(index="wildchat_aqa_summary")
    print("Connected to ElasticSearch")

    if client.indices.exists(index=args.index_name):
        client.indices.delete(index=args.index_name)
    print("Existing index deleted.")

    # Disable refresh interval and replicas for faster bulk indexing.
    index_body = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "refresh_interval": -1,
            "analysis": {
                "tokenizer": {"icu_tokenizer": {"type": "icu_tokenizer"}},
                "analyzer": {
                    "icu_analyzer": {
                        "type": "custom",
                        "tokenizer": "icu_tokenizer",
                        "filter": ["icu_folding"],
                    }
                },
            },
        },
        "mappings": {
            "properties": {
                "document": {"type": "text", "analyzer": "icu_analyzer"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": args.embedding_dim,
                    "index": True,
                    "similarity": "cosine",
                },
                "hash": {"type": "keyword"},
                "unique_id": {"type": "keyword"},
                "timestamp": {
                    "type": "date",
                    "format": "strict_date_optional_time||epoch_millis",
                },
                "user_name": {"type": "keyword"},
                "country": {"type": "keyword"},
            }
        },
    }
    client.indices.create(index=args.index_name, body=index_body, request_timeout=60)
    print("Index created.")

    documents = documents.map(
        es_index_worker,
        fn_kwargs={
            "index_name": args.index_name,
            "embedding_dim": args.embedding_dim,
        },
        batched=True,
        num_proc=16,
        batch_size=4096,
        # batch_size=len(documents) // os.cpu_count() + 1,
        with_rank=True,
    )
    # Re-enable refresh interval after bulk indexing.
    client.indices.put_settings(
        index=args.index_name, body={"index": {"refresh_interval": "1s"}}
    )
    print("Settings restored.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_path",
        type=str,
        default="dataset/wildchat_aqa_document_with_embedding",
    )
    parser.add_argument(
        "--index_name", type=str, default="wildchat_aqa_document"
    )
    parser.add_argument("--embedding_dim", type=int, default=3072)
    args = parser.parse_args()
    main(args)
