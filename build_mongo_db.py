import os
import json
import datetime
import argparse
import datasets
from tqdm import tqdm
from pymongo import MongoClient

DB_NAME = "wildchat-aqa-db"
COLLECTION_NAME = "wildchat"


def get_start_of_week(date):
    # Find the difference from the start of the week (Monday)
    start_of_week = date - datetime.timedelta(
        days=date.weekday()
    )  # .weekday() gives Monday as 0

    return datetime.datetime.strptime(start_of_week.strftime("%Y-%m-%d"), "%Y-%m-%d")


def get_start_of_month(date):

    # Create a new date with the same year and month, but set the day to 1
    start_of_month = datetime.datetime(date.year, date.month, 1)

    # Format the date to "YYYY-mm-dd"
    return start_of_month


def process_data(data):
    conversation = json.dumps(
        [{"content": x["content"], "role": x["role"]} for x in data["conversation"]]
    )
    user_name = data["user_name"]
    date_time = data["timestamp"]
    cid = data["conversation_id"]
    level_1_label = [str(x) for x in data["classes_level_1"]]
    level_2_label = []
    cur_level_2_label_raw = data["classes_level_2"]
    for l1_label in level_1_label:
        for l2_label in cur_level_2_label_raw[int(l1_label)]:
            level_2_label.append(f"{l1_label}.{l2_label}")

    summary = data["summary"]
    hash_val = data["hash"]
    keywords = data["keywords"]
    keywords_aggregated = data["keywords_aggregated"]
    language = data["attributes"]["language"][0]
    country = data["conversation"][0]["country"]
    reigon = data["conversation"][0]["state"]

    deduped_keywords = []
    dedup_set = set()
    for kw in keywords:
        if kw["value"].lower() not in dedup_set:
            dedup_set.add(kw["value"].lower())
            deduped_keywords.append(kw)
    keywords = deduped_keywords

    return {
        "conversation": conversation,
        "user_name": user_name,
        "timestamp": date_time,
        "time_day": datetime.datetime.strptime(
            date_time.strftime("%Y-%m-%d"), "%Y-%m-%d"
        ),
        "time_week": get_start_of_week(date_time),
        "time_month": get_start_of_month(date_time),
        "hash": hash_val,
        "converstation_id": cid,
        "labels": level_1_label + level_2_label,
        "label_level_1": level_1_label,
        "label_level_2": level_2_label,
        "keywords": [
            {
                "description": kw["description"],
                "keyword_type": kw["keyword_type"],
                "value": kw["value"].lower(),
            }
            for kw in keywords
        ],
        "keywords_aggregated": [
            {
                "keyword_type": kw["keyword_type"],
                "value": kw["value"],
            }
            for kw in keywords_aggregated
        ],
        "language": language,
        "summary": summary,
        "country": country,
        "reigon": reigon,
        "token_count": data["token_count"],
    }


def create_main_db(collection, result):
    result_list = list(result)

    print(len(result_list))

    collection.drop()
    collection.insert_many(result_list)

    print(collection.count_documents({}))

    collection.create_index(
        {
            "labels": 1,
            "language": 1,
            "country": 1,
            "timestamp": 1,
            "user_name": 1,
            "time_week": 1,
            "hash": 1,
        },
        unique=True,
    )

    collection.create_index(
        {
            "label_level_1": 1,
            "language": 1,
            "country": 1,
            "timestamp": 1,
            "time_week": 1,
            "user_name": 1,
            "hash": 1,
        },
        unique=True,
    )

    collection.create_index(
        {
            "label_level_2": 1,
            "language": 1,
            "country": 1,
            "timestamp": 1,
            "user_name": 1,
            "time_week": 1,
            "hash": 1,
        },
        unique=True,
    )

    collection.create_index(
        {
            "keywords_aggregated.value": 1,
            "language": 1,
            "country": 1,
            "timestamp": 1,
            "user_name": 1,
            "time_week": 1,
            "hash": 1,
        },
        unique=True,
    )

    collection.create_index("hash", unique=True)
    collection.create_index("converstation_id", unique=True)
    collection.create_index("user_name")
    collection.create_index("timestamp")
    collection.create_index("time_day")
    collection.create_index("time_week")
    collection.create_index("time_month")
    collection.create_index("labels")
    collection.create_index("language")
    collection.create_index("country")
    collection.create_index("reigon")
    collection.create_index("keywords.value")
    collection.create_index("keywords_aggregated.value")
    collection.create_index("label_level_1")
    collection.create_index("label_level_2")
    print("Indexing done")
    print("Creating text index")
    print(collection.count_documents({}))


def main(args):
    client = MongoClient("localhost", 27017)
    data = datasets.Dataset.load_from_disk(args.data_path)
    result = data.map(
        process_data, num_proc=os.cpu_count(), remove_columns=data.column_names
    )

    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    create_main_db(collection, result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_path",
        type=str,
        default="dataset/wildchat_aqa",
    )
    args = parser.parse_args()
    main(args)
