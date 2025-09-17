import os
import json
import datetime
import argparse
import datasets
from pymongo import MongoClient
from build_mongo_db import DB_NAME

QA_COLLECTION_NAME = "wildchat-qa"


def main(args):
    client = MongoClient("localhost", 27017)
    data = datasets.Dataset.load_from_disk(args.data_path)
    
    # we only need these for mongo db
    
    columns_to_keep = [
        'condition_type', 'condition_value', 'target_type', 'target_candidates', 'keywords_type', 'hash', 'question', 'options', 'option_weights'
    ]

    columns_to_remove = [col for col in data.column_names if col not in columns_to_keep]

    data_new = data.remove_columns(columns_to_remove)

    collection = client[DB_NAME][QA_COLLECTION_NAME]
    collection.drop()
    collection.insert_many(data_new)
    collection.create_index("hash", unique=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_path",
        type=str,
        default="dataset/wildchat_aqa_with_embedding_and_gpt_generated_query",
        help="Path to the data samples",
    )

    args = parser.parse_args()
    main(args)
