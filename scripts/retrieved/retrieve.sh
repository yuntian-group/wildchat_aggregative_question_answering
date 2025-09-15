source init.sh 
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/bm25_raw_retrieve_sampled.yaml --mode retrieve
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/bm25_summary_retrieve_sampled.yaml --mode retrieve
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/vector_raw_retrieve_sampled.yaml --mode retrieve
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/vector_summary_retrieve_sampled.yaml --mode retrieve