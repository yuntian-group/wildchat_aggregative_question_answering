import os
import json
from datetime import datetime, timedelta
from modeling.rag_model import RetrieverBase

DEFAULT_START_TIME = "04-08-2023"
DEFAULT_END_TIME = "05-01-2024"
MAX_QUERY = 10


def build_filter(generated_request):
    start_date = generated_request.get("start_time", DEFAULT_START_TIME)
    end_date = generated_request.get("end_time", DEFAULT_END_TIME)
    country = generated_request.get("country", [])
    user_name = generated_request.get("user_name", [])

    if start_date.strip() == "":
        start_date = DEFAULT_START_TIME
    if end_date.strip() == "":
        end_date = DEFAULT_END_TIME

    start_date_datetime = datetime.strptime(start_date, "%m-%d-%Y")
    end_date_datetime = datetime.strptime(end_date, "%m-%d-%Y")

    ed_time = end_date_datetime + timedelta(days=1)

    all_filters = [
        {
            "range": {
                "timestamp": {
                    "gte": start_date_datetime.isoformat() + "Z",
                    "lt": ed_time.isoformat() + "Z",
                }
            }
        }
    ]

    if len(country) > 0:
        all_filters.append({"terms": {"country": country}})

    if len(user_name) > 0:
        all_filters.append({"terms": {"user_name": user_name}})

    return all_filters


class ModelGeneratedQueryRAGRetriever(RetrieverBase):
    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)
