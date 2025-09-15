source init.sh
wandb online
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gemma3-4b/oracle_gemma3-4b_5_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gemma3-4b/oracle_gemma3-4b_10_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gemma3-4b/oracle_gemma3-4b_20_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gemma3-4b/oracle_gemma3-4b_50_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gemma3-4b/oracle_gemma3-4b_100_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gemma3-4b/oracle_gemma3-4b_200_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/gemma3-4b/oracle_gemma3-4b_500_summary_rank_sampled.yaml