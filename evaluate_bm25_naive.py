import os
import argparse
import datasets
from rank_bm25 import BM25Okapi
from evaluation import compute_metrics


def bm25_baseline(examples):
    all_questions = examples["question"]
    all_options = examples["options"]

    ret = []

    for i in range(len(all_questions)):
        question = all_questions[i]
        options = all_options[i]

        tokenized_corpus = [doc.split() for doc in options]
        bm25 = BM25Okapi(tokenized_corpus)

        tokenized_query = question.split()
        scores = bm25.get_scores(tokenized_query)

        scores.tolist()
        s_idx = [(x, i) for i, x in enumerate(scores)]
        s_idx = sorted(s_idx, key=lambda x: x[0], reverse=True)
        preds = [int(x[1]) for x in s_idx]
        ret.append(preds)
    return {"preds": ret}

        


def main(args):
    d = datasets.Dataset.load_from_disk(args.data_path)
    preds = d.map(bm25_baseline, batched=True, batch_size=len(d) // os.cpu_count() or 1, remove_columns=d.column_names, num_proc=os.cpu_count())
    all_options = d["option_weights"]
    all_preds = preds["preds"]

    print(compute_metrics(all_options, all_preds))


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
