source init.sh
wandb online
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-8b-think/vector_raw/vector_qwen3-8b-think_5_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-8b-think/vector_raw/vector_qwen3-8b-think_10_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-8b-think/vector_raw/vector_qwen3-8b-think_20_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-8b-think/vector_raw/vector_qwen3-8b-think_50_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-8b-think/vector_raw/vector_qwen3-8b-think_100_rank_sampled.yaml