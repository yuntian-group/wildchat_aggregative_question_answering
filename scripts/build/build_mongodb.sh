#!/bin/bash
source init.sh
python3 build_mongo_db.py --data_path dataset/wildchat_aqa_conversations
python3 build_qa_mongo_db.py --data_path dataset/wildchat_aqa_with_embedding_and_gpt_generated_query