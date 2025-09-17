import yaml
import json
import uvicorn
import datasets
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime, timedelta
from build_qa_mongo_db import QA_COLLECTION_NAME
from concurrent.futures import ThreadPoolExecutor
from fastapi.middleware.cors import CORSMiddleware
from build_mongo_db import DB_NAME, COLLECTION_NAME


TAXONOMY_CONFIG_PATH = "data_visualize/backend/config.yaml"

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://localhost:8000",
    # "http://65.108.32.135:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open(TAXONOMY_CONFIG_PATH) as f:
    config = yaml.safe_load(f)

level_1_taxonomy_path = config["level_1_taxonomy_path"]
level_2_taxonomy_path = config["level_2_taxonomy_path"]

with open(level_1_taxonomy_path) as f:
    taxonomies = [
        {"class_name": x["class_name"], "index": str(x["index"])}
        for x in json.load(f)["classes"]
    ]

taxonomies = sorted(taxonomies, key=lambda x: int(x["index"]))

client = MongoClient("localhost", 27017)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
qa_collection = db[QA_COLLECTION_NAME]

# Get all countries order by frequency
all_countries_with_frequency = collection.aggregate(
    [
        {"$unwind": "$country"},
        {"$group": {"_id": "$country", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
)

# Get all languages order by frequency
all_languages_with_frequency = collection.aggregate(
    [
        {"$unwind": "$language"},
        {"$group": {"_id": "$language", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
)

# Get top 20 user list
initial_users_with_frequency = collection.aggregate(
    [
        {"$group": {"_id": "$user_name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20},
    ]
)

# Get top 50 keywords

initial_keywords_with_frequency = collection.aggregate(
    [
        {"$unwind": "$keywords"},
        {
            "$group": {
                "_id": "$keywords.value",
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": 50},
    ]
)

initial_keywords_aggregated_with_frequency = collection.aggregate(
    [
        {"$unwind": "$keywords_aggregated"},
        {
            "$group": {
                "_id": "$keywords_aggregated.value",
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": 50},
    ]
)


all_countries_tmp = [x["_id"] for x in all_countries_with_frequency]
all_languages_tmp = [x["_id"] for x in all_languages_with_frequency]
initial_users_tmp = [x["_id"] for x in initial_users_with_frequency]
initial_keywords_tmp = [x["_id"] for x in initial_keywords_with_frequency]
initial_keywords_aggregated_tmp = [
    x["_id"] for x in initial_keywords_aggregated_with_frequency
]

print(all_countries_tmp)
print("lang", all_languages_tmp)
print("user", initial_users_tmp)
print("keywords", initial_keywords_tmp)
print("keywords_agg", initial_keywords_aggregated_tmp)

all_countries = []
all_languages = []
initial_users = []

for country in all_countries_tmp:
    if country is not None:
        all_countries.append(country)

for language in all_languages_tmp:
    if language is not None:
        all_languages.append(language)

for user in initial_users_tmp:
    if user is not None:
        initial_users.append(user)

for idx, x in enumerate(taxonomies):
    cur_index = x["index"]
    if cur_index in level_2_taxonomy_path:
        with open(level_2_taxonomy_path[cur_index]) as f:
            taxonomies[idx]["sub_classes"] = sorted(
                [
                    {"class_name": y["class_name"], "index": str(y["index"])}
                    for y in json.load(f)["classes"]
                ],
                key=lambda y: int(y["index"]),
            )
    else:
        taxonomies[idx]["sub_classes"] = []



@app.get("/")
def read_root():
    return {"Hello": "UNWORLDS"}


@app.get("/get_label_hierarchy")
def get_label_hierarchy():
    return taxonomies


@app.get("/get_all_country")
def get_all_country():
    return all_countries


@app.get("/get_all_language")
def get_all_language():
    return all_languages


@app.get("/get_user_list")
def get_user_list(query: str = None):
    if query is not None and query != "":
        cur_user_result_tmp = collection.aggregate(
            [
                {"$match": {"user_name": {"$regex": query, "$options": "i"}}},
                {"$group": {"_id": "$user_name", "count": {"$sum": 1}}},
                {"$addFields": {"relevance": {"$indexOfCP": ["$_id", query]}}},
                {
                    "$sort": {"relevance": 1, "count": -1}
                },  # Sort by relevance and then by frequency
                {"$limit": 20},
            ]
        )
        cur_user_result = [x["_id"] for x in cur_user_result_tmp]
        print(cur_user_result)
        return cur_user_result
    else:
        print(initial_users)
        return initial_users


@app.get("/get_keywords_list")
def get_keywords_list(query: str = None):
    if query is not None and query != "":
        cur_keyworkds_result_tmp = collection.aggregate(
            [
                {"$unwind": "$keywords"},
                {"$match": {"keywords.value": {"$regex": query, "$options": "i"}}},
                {"$group": {"_id": "$keywords.value", "count": {"$sum": 1}}},
                {"$addFields": {"relevance": {"$indexOfCP": ["$_id", query]}}},
                {
                    "$sort": {"relevance": 1, "count": -1}
                },  # Sort by relevance and then by frequency
                {"$limit": 100},
            ]
        )
        cur_keywords_result = [x["_id"] for x in cur_keyworkds_result_tmp]
        print(cur_keywords_result)
        return cur_keywords_result
    else:
        return initial_keywords_tmp


@app.get("/get_keywords_aggregated_list")
def get_keywords_aggregated_list(query: str = None):
    if query is not None and query != "":
        cur_keyworkds_result_tmp = collection.aggregate(
            [
                {"$unwind": "$keywords_aggregated"},
                {
                    "$match": {
                        "keywords_aggregated.value": {"$regex": query, "$options": "i"}
                    }
                },
                {"$group": {"_id": "$keywords_aggregated.value", "count": {"$sum": 1}}},
                {"$addFields": {"relevance": {"$indexOfCP": ["$_id", query]}}},
                {
                    "$sort": {"relevance": 1, "count": -1}
                },  # Sort by relevance and then by frequency
                {"$limit": 100},
            ]
        )
        cur_keywords_result = [x["_id"] for x in cur_keyworkds_result_tmp]
        print(cur_keywords_result)
        return cur_keywords_result
    else:
        return initial_keywords_aggregated_tmp


class DialogueRequest(BaseModel):
    country: List[str]
    region: List[str]
    user_name: List[str]
    language: List[str]
    topics: List[str]
    start_date: str
    end_date: str
    keywords: List[str]
    keywords_aggregated: List[str]
    page: int
    page_size: int


@app.get("/get_dialogue_context_by_question_hash")
def get_dialogue_context_by_question_hash(hash: str):
    print(hash)
    result = qa_collection.aggregate([{"$match": {"hash": hash}}])
    res = list(result)

    # print(res)

    ret = res[0]
    condition_type = ret["condition_type"]
    condition_value = ret["condition_value"]

    dial_req = DialogueRequest(
        country=[],
        region=[],
        user_name=[],
        language=[],
        topics=[],
        start_date="",
        end_date="",
        keywords=[],
        keywords_aggregated=[],
        page=0,
        page_size=10,
    )

    for i in range(len(condition_type)):
        if condition_type[i] == "country":
            dial_req.country.append(condition_value[i])
        if condition_type[i] == "region":
            dial_req.region.append(condition_value[i])
        if condition_type[i] == "user_name":
            dial_req.user_name.append(condition_value[i])
        if condition_type[i] == "language":
            dial_req.language.append(condition_value[i])
        if condition_type[i] == "label_level_1":
            dial_req.topics.append(condition_value[i])
        if condition_type[i] == "label_level_2":
            dial_req.topics.append(condition_value[i])
        if condition_type[i] == "keywords":
            dial_req.keywords.append(condition_value[i])
        if condition_type[i] == "keywords_aggregated":
            dial_req.keywords_aggregated.append(condition_value[i])
        if condition_type[i] == "time_week":
            if condition_value[i].find(":") != -1:
                dial_req.start_date = condition_value[i].split()[0]
                dial_req.end_date = (
                    datetime.strptime(dial_req.start_date, "%Y-%m-%d")
                    + timedelta(days=7)
                ).strftime("%Y-%m-%d")
            else:
                dial_req.start_date = condition_value[i]
                dial_req.end_date = (
                    datetime.strptime(condition_value[i], "%Y-%m-%d")
                    + timedelta(days=7)
                ).strftime("%Y-%m-%d")

    return get_dialogues(dial_req)


@app.post("/get_dialgoues")
def get_dialogues(
    request: DialogueRequest,
):
    # query mongo db based on the request, each field in the request is a list of values, the values are ORed
    query = {}
    if len(request.country) > 0:
        query["country"] = {"$in": request.country}
    if len(request.region) > 0:
        query["region"] = {"$in": request.region}
    if len(request.user_name) > 0:
        query["user_name"] = {"$in": request.user_name}
    if len(request.language) > 0:
        query["language"] = {"$in": request.language}
    if len(request.topics) > 0:
        if len(request.topics) > 1:
            query["labels"] = {"$all": request.topics}
        else:
            query["labels"] = {"$in": request.topics}
    if len(request.keywords) > 0:
        query["keywords.value"] = {"$in": request.keywords}

    if len(request.keywords_aggregated) > 0:
        query["keywords_aggregated.value"] = {"$in": request.keywords_aggregated}

    if request.start_date and request.end_date:
        request.start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        request.end_date = datetime.strptime(request.end_date, "%Y-%m-%d")

        query["timestamp"] = {
            "$gte": request.start_date,
            "$lte": request.end_date,
        }

    print(query)

    # query.pop("timestamp", None)
    # request.page_size = 2

    # print(query)

    skip = request.page * request.page_size

    def count_dialogues():
        return collection.count_documents(query)

    def token_count_dialogues():
        cur_result = collection.aggregate(
            [
                {"$match": query},
                {"$group": {"_id": None, "total": {"$sum": "$token_count"}}},
            ]
        )

        cur_result_list = list(cur_result)

        if len(cur_result_list) == 0:
            return 0
        return cur_result_list[0]["total"]

    def get_dialogue_result():
        cur_result = list(
            collection.aggregate(
                [
                    {"$match": query},
                    {"$sort": {"timestamp": -1}},
                    {"$limit": 200},
                ],
            )
        )
        ret = [
            {
                "conversation": json.loads(x["conversation"]),
                "summary": x["summary"],
                "user_name": x["user_name"],
                "timestamp": x["timestamp"],
                "labels": x["labels"],
                "hash": x["hash"],
                "keywords": x["keywords"],
                "keywords_aggregated": x["keywords_aggregated"],
            }
            for x in cur_result
        ]
        return ret

    def get_country_stats():
        cur_result = list(
            collection.aggregate(
                [
                    {"$match": query},
                    {"$group": {"_id": "$country", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ]
            )
        )
        ret = [(x["_id"], x["count"]) for x in cur_result]
        return ret

    def get_region_stats():
        cur_result = list(
            collection.aggregate(
                [
                    {"$match": query},
                    {"$group": {"_id": "$region", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ]
            )
        )
        ret = [(x["_id"], x["count"]) for x in cur_result]
        return ret

    def get_user_stats():
        cur_result = list(
            collection.aggregate(
                [
                    {"$match": query},
                    {"$group": {"_id": "$user_name", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 100},
                ]
            )
        )
        ret = [(x["_id"], x["count"]) for x in cur_result]
        return ret

    def get_language_stats():
        cur_result = list(
            collection.aggregate(
                [
                    {"$match": query},
                    {"$group": {"_id": "$language", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ]
            )
        )
        ret = [(x["_id"], x["count"]) for x in cur_result]
        return ret

    def get_label_stats():
        cur_result = list(
            collection.aggregate(
                [
                    {"$match": query},
                    {"$unwind": "$labels"},
                    {"$group": {"_id": "$labels", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ]
            )
        )
        ret = [(x["_id"], x["count"]) for x in cur_result]
        return ret

    def get_keyword_stats():
        cur_result = list(
            collection.aggregate(
                [
                    {"$match": query},
                    {"$unwind": "$keywords"},
                    {
                        "$group": {
                            "_id": {
                                "$concat": [
                                    "$keywords.value",
                                    ":",
                                    "$keywords.keyword_type",
                                ]
                            },
                            "count": {"$sum": 1},
                        }
                    },
                    {"$sort": {"count": -1}},
                    {"$limit": 100},
                ]
            )
        )
        ret = [(x["_id"], x["count"]) for x in cur_result]
        return ret

    def get_keyword_aggregated_stats():
        cur_result = list(
            collection.aggregate(
                [
                    {"$match": query},
                    {"$unwind": "$keywords_aggregated"},
                    {
                        "$group": {
                            "_id": {
                                "$concat": [
                                    "$keywords_aggregated.value",
                                    ":",
                                    "$keywords_aggregated.keyword_type",
                                ]
                            },
                            "count": {"$sum": 1},
                        }
                    },
                    {"$sort": {"count": -1}},
                    {"$limit": 100},
                ]
            )
        )
        ret = [(x["_id"], x["count"]) for x in cur_result]
        return ret

    def get_keyword_aggregated_count_stats():
        curq = {**query, "keywords_aggregated": {"$exists": True, "$not": {"$size": 0}}}
        ret = collection.count_documents(curq)
        return ret

    def get_time_stats():
        cur_result = list(
            collection.aggregate(
                [
                    {"$match": query},
                    {
                        "$group": {
                            "_id": {
                                "$dateToString": {
                                    "format": "%Y-%m-%d",
                                    "date": "$time_week",
                                }
                            },
                            "count": {"$sum": 1},
                        }
                    },
                    {"$sort": {"_id": 1}},
                ]
            )
        )
        ret = [(x["_id"], x["count"]) for x in cur_result]
        return ret

    with ThreadPoolExecutor() as executor:
        token_count_dialogues_future = executor.submit(token_count_dialogues)
        dialogue_count_future = executor.submit(count_dialogues)
        result = executor.submit(get_dialogue_result)
        country_stats_future = executor.submit(get_country_stats)
        user_stats_future = executor.submit(get_user_stats)
        language_stats_future = executor.submit(get_language_stats)
        label_stats_future = executor.submit(get_label_stats)
        keyword_stats_future = executor.submit(get_keyword_stats)
        keyword_aggregated_stats_future = executor.submit(get_keyword_aggregated_stats)
        kw_dialogue_cnt_future = executor.submit(get_keyword_aggregated_count_stats)
        time_stats_future = executor.submit(get_time_stats)

        result = result.result()
        dialogue_count = dialogue_count_future.result()
        country_stats = country_stats_future.result()
        user_stats = user_stats_future.result()
        language_stats = language_stats_future.result()
        label_stats = label_stats_future.result()
        keyword_stats = keyword_stats_future.result()
        time_stats = time_stats_future.result()
        kw_dialogue_cnt = kw_dialogue_cnt_future.result()

    level_0_status = []
    level_1_status = {}

    print(label_stats)

    for x in label_stats:
        if x[0].find(".") == -1:
            level_0_status.append({"topic_id": x[0], "count": x[1]})
        else:
            parent = x[0].split(".")[0]
            if parent not in level_1_status:
                level_1_status[parent] = []
            level_1_status[parent].append({"topic_id": x[0], "count": x[1]})

    ret = {
        "dialogues": result,
        "country_stats": [
            {"country/reigon": x[0], "count": x[1]} for x in country_stats
        ],
        "user_stats": [{"user_name": x[0], "count": x[1]} for x in user_stats],
        "language_stats": [{"language": x[0], "count": x[1]} for x in language_stats],
        "label_stats_level_0": level_0_status,
        "label_stats_level_1": level_1_status,
        "keyword_stats": [{"keyword": x[0], "count": x[1]} for x in keyword_stats],
        "keyword_aggregated_stats": [
            {"keyword_aggregated": x[0], "count": x[1]}
            for x in keyword_aggregated_stats_future.result()
        ],
        "time_stats": [{"date": time, "count": count} for time, count in time_stats],
        "dialogue_count": dialogue_count,
        "token_count": token_count_dialogues_future.result(),
        "num_page": dialogue_count // request.page_size
        + int(dialogue_count % request.page_size > 0),
    }

    # compute percentage for country, user, language, label_0, label_1, keyword

    total = dialogue_count
    for x in ret["country_stats"]:
        x["percentage"] = x["count"] / total * 100
    for x in ret["user_stats"]:
        x["percentage"] = x["count"] / total * 100
    for x in ret["language_stats"]:
        x["percentage"] = x["count"] / total * 100
    for x in ret["label_stats_level_0"]:
        x["percentage"] = x["count"] / total * 100

    label_level_0_count_dict = {
        x["topic_id"]: x["count"] for x in ret["label_stats_level_0"]
    }
    for parent, children in ret["label_stats_level_1"].items():
        for x in children:
            x["percentage"] = x["count"] / label_level_0_count_dict[parent] * 100

    for x in ret["keyword_stats"]:
        x["percentage"] = x["count"] / total * 100

    for x in ret["keyword_aggregated_stats"]:
        x["percentage"] = x["count"] / total * 100

    print(
        "kw pct",
        kw_dialogue_cnt,
        total,
        (kw_dialogue_cnt + 1e-6) / (total + 1e-6) * 100,
    )

    return ret


@app.get("/get_question_list")
def get_question_list(condition: str = "", target: str = ""):

    match_query = {}
    if condition != "":
        condition_list = condition.split(",")

        if (
            len(condition_list) > 1
            and len(set(condition_list)) == 1
            and condition_list[0]
            in {
                "label_level_1",
                "label_level_2",
                "user_name",
            }
        ):
            match_query["condition_type"] = condition_list
        else:
            match_query["condition_type"] = {
                "$all": condition_list,
                "$size": len(condition_list),
            }
    if target != "":
        match_query["target_type"] = target

    print(match_query)

    result = qa_collection.aggregate(
        [
            {"$match": match_query},
            {"$project": {"hash": "$hash", "question": 1}},
        ]
    )

    ret = [{"hash": x["hash"], "question": x["question"]} for x in result]

    return list(ret)


@app.get("/get_question_by_hash")
def get_question_by_hash(hash: str):

    projection_instruction = {
        "$project": {
            "_id": 0,
            "hash": "$hash",
            "question": 1,
            "options": 1,
            "option_weights": 1,
            "target_type": 1,
            "condition_type": 1,
            "condition_value": 1,
        }
    }

    if hash is None or hash == "":
        result = qa_collection.aggregate(
            [
                {"$match": {}},
                {"$limit": 1},
                projection_instruction,
            ]
        )
    else:
        result = qa_collection.aggregate(
            [
                {"$match": {"hash": hash}},
                projection_instruction,
            ]
        )
    ret = list(result)[0]

    return ret


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
