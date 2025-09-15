source init.sh
wandb online
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/qwen3-32b/oracle_qwen3-32b_500_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/qwen3-32b/oracle_qwen3-32b_200_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/qwen3-32b/oracle_qwen3-32b_100_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/qwen3-32b/oracle_qwen3-32b_5_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/qwen3-32b/oracle_qwen3-32b_10_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/qwen3-32b/oracle_qwen3-32b_20_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/qwen3-32b/oracle_qwen3-32b_50_summary_rank_sampled.yaml


