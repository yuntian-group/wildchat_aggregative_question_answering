import random
import logging
import datasets
from typing import List
from typing import Optional
from torch.utils.data import Dataset
from utils.utils import summary_with_meta_data, time_decode
from transformers import PreTrainedTokenizer, AutoTokenizer


class WildChatAQADataset(Dataset):
    def __init__(
        self,
        data_path: str,
        tokenizer: Optional[PreTrainedTokenizer] = None,
        summary: Optional[bool] = False,
    ):
        super().__init__()
        self.datasets = datasets.Dataset.load_from_disk(data_path)
        self.tokenizer = tokenizer
        self.summary = summary

    def __len__(self):
        return len(self.datasets)

    def _build_conv_raw(self, cur_data):
        time = cur_data["timestamp"]
        time_str = time_decode(time)
        conv = cur_data["conversation"]
        new_conv = [
            {
                "role": "system",
                "content": "Time: {}, user {} is from {}.".format(
                    time_str,
                    cur_data["user_name"],
                    cur_data["conversation"][0]["country"],
                ),
            }
        ]
        user_name = cur_data["user_name"]
        for idx, turn in enumerate(conv):
            if idx % 2 == 0:
                new_conv.append(
                    {
                        "content": "User {}: {}".format(user_name, turn["content"]),
                        "role": "user",
                    }
                )
            else:
                new_conv.append(
                    {
                        "content": "Assistant: {}".format(turn["content"]),
                        "role": "assistant",
                    }
                )
        return new_conv

    def _build_conv_summary(self, cur_data):
        time = cur_data["timestamp"]
        time_str = time_decode(time)
        user_name = cur_data["user_name"]
        new_conv = [
            {
                "role": "system",
                "content": "Time: {}, user {} is from {}.".format(
                    time_str,
                    user_name,
                    cur_data["conversation"][0]["country"],
                ),
            },
            {
                "role": "user",
                "content": "User {}: {}".format(user_name, cur_data["summary"]),
            },
        ]

        return new_conv

    def __getitem__(self, index):
        cur_data = self.datasets[index]

        if not self.summary:
            new_conv = self._build_conv_raw(cur_data)
        else:
            new_conv = self._build_conv_summary(cur_data)

        if self.tokenizer.name_or_path.lower().find("qwen3"):
            text = self.tokenizer.apply_chat_template(
                new_conv, tokenize=False, enable_thinking=False
            )
        else:
            text = self.tokenizer.apply_chat_template(new_conv, tokenize=False)
        return text


class WildChatAQACollator:
    def __init__(self, tokenizer: PreTrainedTokenizer, max_length: int = 8192):
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __call__(self, batch: List[str]):
        tokenized_batch = self.tokenizer(
            batch,
            padding=True,
            truncation=True,
            padding_side="left",
            return_tensors="pt",
            max_length=self.max_length,
        )

        labels = tokenized_batch["input_ids"].clone()
        labels[labels == self.tokenizer.pad_token_id] = -100
        tokenized_batch["labels"] = labels

        return tokenized_batch


if __name__ == "__main__":
    d = WildChatAQADataset(
        data_path="dataset/wildchat_data_understanding_keywords_aggregated",
        tokenizer=AutoTokenizer.from_pretrained("Qwen/Qwen3-8B"),
        summary=False,
    )
    for i in range(10):
        print(d[i])
        input()
