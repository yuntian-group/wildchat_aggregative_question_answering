source init.sh
wandb online
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gpt-4.1-mini/oracle_gpt-4.1-mini_5_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gpt-4.1-mini/oracle_gpt-4.1-mini_500_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gpt-4.1-mini/oracle_gpt-4.1-mini_200_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gpt-4.1-mini/oracle_gpt-4.1-mini_10_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gpt-4.1-mini/oracle_gpt-4.1-mini_20_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gpt-4.1-mini/oracle_gpt-4.1-mini_50_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gpt-4.1-mini/oracle_gpt-4.1-mini_100_summary_rank_sampled.yaml

