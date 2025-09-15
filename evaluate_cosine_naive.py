import os
import hashlib
import argparse
import datasets
import tiktoken
from evaluation import compute_metrics
from utils.utils import parse_embedding_output
from utils.openai_batch_request import OpenAIBatchRequestWithFileProcessing

def cosine_score_baseline(examples, hash_to_embedding):

    all_question_embeddings = examples["question_embedding"]
    all_options = examples["options"]

    all_preds = []

    for i in range(len(all_question_embeddings)):
        question_embedding = list(all_question_embeddings[i])
        options = all_options[i]


        scores = []
        for option in options:
            o_hash = hashlib.md5(option.encode("utf-8")).hexdigest()
            try:
                option_embedding = hash_to_embedding[o_hash]
            except:
                print(f"Option not found in hash_to_embedding: {option}")
                option_embedding = [0.0]*1536

            score = sum([a*b for a, b in zip(question_embedding, option_embedding)])
            scores.append(score)

        s_idx = [(x, i) for i, x in enumerate(scores)]
        s_idx = sorted(s_idx, key=lambda x: x[0], reverse=True)
        preds = [int(x[1]) for x in s_idx]
        all_preds.append(preds)
    return {"preds": all_preds}


def build_options_embeddings(all_options):

    all_options_set = set()

    for options in all_options:
        for option in options:
            all_options_set.add(option)

    log_path = "logs/naive_cosine_sim"
    
    requestor = OpenAIBatchRequestWithFileProcessing(
        log_path, os.environ["OPENAI_API_KEY"], chunk_size=2048
    )

    all_requests = [
        {
            "custom_id": hashlib.md5(x.encode("utf-8")).hexdigest(),
            "method": "POST",
            "url": "/v1/embeddings",
            "body": {
                "input": x,
                "model": "text-embedding-3-large",
                "encoding_format": "float",
            },
        }
        for x in all_options_set
    ]

    requestor.do_batch_request(all_requests, "/v1/embeddings")
    hash_to_embedding = parse_embedding_output(log_path)

    return hash_to_embedding



def main(args):
    d = datasets.Dataset.load_from_disk(args.data_path)
    all_options = d["options"]
    hash_to_embeddings = build_options_embeddings(all_options)

    preds = d.map(cosine_score_baseline,
                  fn_kwargs={"hash_to_embedding": hash_to_embeddings},
                  batched=True, 
                  batch_size=len(d) // os.cpu_count() or 1, 
                  remove_columns=d.column_names, 
                  num_proc=os.cpu_count())
    all_options = d["option_weights"]
    all_preds = preds["preds"]
    print(compute_metrics(all_preds, all_options))
    

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
