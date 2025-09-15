source init.sh
wandb online
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/gpt-4.1-mini/model_generated_vector_raw/model_generated_vector_gpt-4.1-mini_100_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/gpt-4.1-mini/model_generated_vector_raw/model_generated_vector_gpt-4.1-mini_50_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/gpt-4.1-mini/model_generated_vector_raw/model_generated_vector_gpt-4.1-mini_20_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/gpt-4.1-mini/model_generated_vector_raw/model_generated_vector_gpt-4.1-mini_10_rank_sampled.yaml
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/gpt-4.1-mini/model_generated_vector_raw/model_generated_vector_gpt-4.1-mini_5_rank_sampled.yaml