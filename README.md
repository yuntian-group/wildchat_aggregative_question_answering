# WildChat AQA #

This is the official repo of paper *From Chat Logs to Collective Insights: Aggregative Question Answering* in EMNLP 2025

[![arXiv](https://img.shields.io/badge/arXiv-2505.23765-b31b1b.svg)](https://arxiv.org/abs/2505.23765)

**Authors:** [Wentao Zhang](https://wentao-zhang.me/), [Woojeong Kim](https://www.wkim.info/), [Yuntian Deng](https://yuntiandeng.com/)



## Dataset ##

## 📂 WildChat-AQA Dataset Releases

- 🤗 **[WildChat-AQA](https://huggingface.co/datasets/ksx-wz/wildchat_aqa_with_embedding_and_gpt_generated_query)**  
  Full dataset with embeddings and PROBE queries.

- 🤗 **[WildChat-AQA-sampled](https://huggingface.co/datasets/ksx-wz/wildchat_aqa_sampled_subset_with_embedding_and_gpt_generated_query)**  
  A sampled subset of WildChat-AQA with embeddings and PROBE queries.

- 🤗 **[WildChat-AQA-conversations](https://huggingface.co/datasets/ksx-wz/wildchat_aqa_conversations)**  
  Raw conversation logs used for aggregation QA tasks.

- 🤗 **[WildChat-AQA-summary-embedding](https://huggingface.co/datasets/ksx-wz/wildchat_aqa_summary_with_embedding)**  
  Summaries of conversations with summary embeddings.

- 🤗 **[WildChat-AQA-conversation-embedding](https://huggingface.co/datasets/ksx-wz/wildchat_aqa_document_with_embedding)**  
  Conversation documents with whole-text embeddings.


## Setup ## 

On a machine with at least **64GB RAM**, perform the following steps:

1. You need to install MongoDB and ElasticSearch to build the retrieval system. You may refer to the official website. 

2. Download dataset and organize them under `dataset` folder like:

```
dataset/
├── wildchat_aqa_conversations/
│ ├── data-00000-of-00003.arrow
│ ├── data-00001-of-00003.arrow
│ ├── data-00002-of-00003.arrow
│ ├── dataset_info.json
│ └── state.json
├── wildchat_aqa_document_with_embedding/
├── wildchat_aqa_sampled_subset_with_embedding_and_gpt_generated_query/
├── wildchat_aqa_summary_with_embedding/
└── wildchat_aqa_with_embedding_and_gpt_generated_query/
```

3. Install all required packages 
```
conda create --name <env> --file requirements.txt
```

4. Modify `init.sh` to fill in proper information needed. Such as ElasticSearch passwords and API keys.

5. In the created environment, make sure ElasticSearch and MongoDB is running properly, run 
```
./scripts/build/build_elastic_search_document.sh
./scripts/build/build_elastic_search_summary.sh
./scripts/build/build_mongodb.sh
```
to build database

6. Run any instructions under `scripts` to perform evaluation, here are explanation of naming rules
    - `oracle` folder: contains all scripts for running evaluation with ground truth 
    - `retrieved` folder: contains all scripts for running RAG-based evaluation including **PROBE**
    - `trained` folder: finetune and evaluation model on conversation datasets
    - Scripts start with `vector`: Dense retrieval approach 
    - Scripts start with `bm25`: BM25 retrieval approach
    - Scripts start with `model_generated`: PROBE-based approach
    - Scripts contain `summary`: use conversation summary as context
    - Scripts contain `raw`: use raw conversation as context 
    - Scripts end with `full`: run on full data, otherwise sampled data 

7. We have already merge the PROBE result into published dataset. But you can also run it on your own with 

```
python3 build_PROBE.py --config <CONFIG_FILE> 
```

Here config files are under `configs/wildchat_aqa` folder, you can use anyone of them, we only read data path from the config and use for logging.


## Visualization Demo ## 

We implemented the demo of this work using a frontend, backend separation parttern, to run the demo, you need to first build up the mongodb using the script mentioned above. 

And then you need to setup the demo via 
```
scripts/visualize/setup_frontend.sh
```

And then run following instructions to start the backend and frontend respectively in two process.

```
scripts/visualize/start_backend.sh
scripts/visualize/start_frontend.sh
```

And the demo will be available on 

```
http://localhost:3000
```


## Citation ##


```
@misc{zhang2025chatlogscollectiveinsights,
      title={From Chat Logs to Collective Insights: Aggregative Question Answering}, 
      author={Wentao Zhang and Woojeong Kim and Yuntian Deng},
      year={2025},
      eprint={2505.23765},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2505.23765}, 
}
```