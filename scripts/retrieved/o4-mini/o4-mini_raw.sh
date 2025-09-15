source init.sh
wandb online
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/o4-mini/vector_raw/vector_o4-mini_100_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/o4-mini/vector_raw/vector_o4-mini_50_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/o4-mini/vector_raw/vector_o4-mini_20_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/o4-mini/vector_raw/vector_o4-mini_10_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/o4-mini/vector_raw/vector_o4-mini_5_rank_sampled.yaml