source init.sh
wandb online
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-8b/vector_summary/vector_qwen3-8b_5_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-8b/vector_summary/vector_qwen3-8b_10_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-8b/vector_summary/vector_qwen3-8b_20_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-8b/vector_summary/vector_qwen3-8b_50_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-8b/vector_summary/vector_qwen3-8b_100_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-8b/vector_summary/vector_qwen3-8b_200_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-8b/vector_summary/vector_qwen3-8b_500_summary_rank_sampled.yaml