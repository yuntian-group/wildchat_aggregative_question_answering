source init.sh 
# python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/model_generated_bm25_raw_retrieve_sampled.yaml --mode retrieve
# python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/model_generated_bm25_summary_retrieve_sampled.yaml --mode retrieve
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/model_generated_vector_raw_retrieve_sampled.yaml --mode retrieve
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/model_generated_vector_summary_retrieve_sampled.yaml --mode retrieve