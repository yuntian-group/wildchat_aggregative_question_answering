source init.sh
wandb online
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/o4-mini/vector_summary/vector_o4-mini_500_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/o4-mini/vector_summary/vector_o4-mini_200_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/o4-mini/vector_summary/vector_o4-mini_100_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/o4-mini/vector_summary/vector_o4-mini_10_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/o4-mini/vector_summary/vector_o4-mini_20_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/o4-mini/vector_summary/vector_o4-mini_50_summary_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/o4-mini/vector_summary/vector_o4-mini_5_summary_rank_sampled.yaml
