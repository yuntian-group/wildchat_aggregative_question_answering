source init.sh
wandb online
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gemma3-4b/oracle_gemma3-4b_5_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gemma3-4b/oracle_gemma3-4b_10_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gemma3-4b/oracle_gemma3-4b_20_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gemma3-4b/oracle_gemma3-4b_50_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gemma3-4b/oracle_gemma3-4b_100_rank_sampled.yaml