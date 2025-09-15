source init.sh 
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/vector_raw_retrieve.yaml --mode retrieve
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/vector_summary_retrieve.yaml --mode retrieve
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/model_generated_vector_raw_retrieve.yaml --mode retrieve
python3 evaluation.py --config_path configs/wildchat_aqa/retrieved/model_generated_vector_summary_retrieve.yaml --mode retrieve