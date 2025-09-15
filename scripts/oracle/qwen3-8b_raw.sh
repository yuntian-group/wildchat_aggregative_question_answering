source init.sh
wandb online
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/qwen3-8b/oracle_qwen3-8b_5_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/qwen3-8b/oracle_qwen3-8b_10_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/qwen3-8b/oracle_qwen3-8b_20_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/qwen3-8b/oracle_qwen3-8b_50_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/qwen3-8b/oracle_qwen3-8b_100_rank_sampled.yaml