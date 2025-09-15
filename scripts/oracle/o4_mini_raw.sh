source init.sh
wandb online
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/o4_mini/oracle_o4_mini_100_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/o4_mini/oracle_o4_mini_50_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/o4_mini/oracle_o4_mini_20_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/o4_mini/oracle_o4_mini_10_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/o4_mini/oracle_o4_mini_5_rank_sampled.yaml