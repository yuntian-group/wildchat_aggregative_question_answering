source init.sh
wandb online
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/qwen3-32b/oracle_qwen3-32b-fp8_100_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/qwen3-32b/oracle_qwen3-32b-fp8_50_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/qwen3-32b/oracle_qwen3-32b-fp8_5_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/qwen3-32b/oracle_qwen3-32b-fp8_10_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/qwen3-32b/oracle_qwen3-32b-fp8_20_rank_sampled.yaml