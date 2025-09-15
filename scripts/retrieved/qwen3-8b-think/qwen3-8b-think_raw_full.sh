source init.sh
wandb online
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-8b-think/vector_raw/vector_qwen3-8b-think_rank.yaml  --data_parallel $1 --data_parallel_rank $2