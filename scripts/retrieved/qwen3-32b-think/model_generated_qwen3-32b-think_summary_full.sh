source init.sh
wandb online
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/qwen3-32b-think/model_generated_vector_summary/model_generated_vector_qwen3-32b-think_summary_rank.yaml --data_parallel $1 --data_parallel_rank $2