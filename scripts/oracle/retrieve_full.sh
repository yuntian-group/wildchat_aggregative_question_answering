source init.sh 
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/raw_retrieve.yaml --mode retrieve
python3 evaluation.py --config_path configs/wildchat_aqa/oracle/summary_retrieve.yaml --mode retrieve