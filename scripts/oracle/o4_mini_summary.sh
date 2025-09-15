source init.sh
wandb online
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/o4_mini/oracle_o4_mini_100_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/o4_mini/oracle_o4_mini_500_summary_rank_sampled.yaml
python3 evaluation.py --config_path  configs/wildchat_aqa/oracle/o4_mini/oracle_o4_mini_200_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/o4_mini/oracle_o4_mini_20_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/o4_mini/oracle_o4_mini_50_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/o4_mini/oracle_o4_mini_10_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/o4_mini/oracle_o4_mini_5_summary_rank_sampled.yaml