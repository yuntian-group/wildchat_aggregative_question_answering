source init.sh
wandb online
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-32b-think/vector_summary/vector_qwen3-32b-think_5_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-32b-think/vector_summary/vector_qwen3-32b-think_10_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-32b-think/vector_summary/vector_qwen3-32b-think_20_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-32b-think/vector_summary/vector_qwen3-32b-think_50_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-32b-think/vector_summary/vector_qwen3-32b-think_100_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-32b-think/vector_summary/vector_qwen3-32b-think_200_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-32b-think/vector_summary/vector_qwen3-32b-think_500_summary_rank_sampled.yaml