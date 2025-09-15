source init.sh 
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/raw_retrieve_sampled.yaml --mode retrieve
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/summary_retrieve_sampled.yaml --mode retrieve