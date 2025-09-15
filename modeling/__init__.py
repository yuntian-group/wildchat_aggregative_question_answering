import torch
import tiktoken
from modeling.rag_model import RAGModel
from transformers import AutoTokenizer
from modeling.bm25_rag_model import BM25Retriver
from modeling.vector_rag_model import VectorDenseRetriever
from modeling.no_rag_model import NoRetriever
from modeling.mongo_db_rag_model import MongoDBRetriever
from modeling.hybrid_rag_model import HybridRetriever
from modeling.model_generated_query_bm25_rag_model import (
    ModelGeneratedQueryBM25RAGRetriever,
)
from modeling.model_generated_query_vector_rag_model import (
    ModelGeneratedQueryVectorRAGRetriever,
)
from modeling.model_generated_query_hybrid_rag_model import (
    ModelGeneratedQueryHybridRAGRetriever,
)
from modeling.vllm_batch_inference_model import VLLMBatchInferenceModel
from modeling.openai_batch_inference_model import OpenAIBatchRequestModel


def build_retriever(**kwargs):

    rag_type = kwargs["rag_type"]
    is_model_generated_retrieval = kwargs.pop("is_model_generated_retrieval", False)

    if rag_type == "bm25":
        if is_model_generated_retrieval:
            retriever = ModelGeneratedQueryBM25RAGRetriever(**kwargs)
        else:
            retriever = BM25Retriver(**kwargs)
    elif rag_type == "vector":
        if is_model_generated_retrieval:
            retriever = ModelGeneratedQueryVectorRAGRetriever(**kwargs)
        else:
            retriever = VectorDenseRetriever(**kwargs)
    elif rag_type == "hybrid":
        if is_model_generated_retrieval:
            retriever = ModelGeneratedQueryHybridRAGRetriever(**kwargs)
        else:
            retriever = HybridRetriever(**kwargs)
    elif rag_type == "none":
        retriever = NoRetriever(**kwargs)
    elif rag_type == "mongodb_gt":
        retriever = MongoDBRetriever(**kwargs)
    else:
        raise ValueError(f"Invalid model type: {rag_type}")

    return retriever


def build_model(model_config: dict):
    model_name = model_config["name"]
    model_type = model_config.get("type", "vllm")
    if model_name in {
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-4.1-nano",
        "gpt-4o",
        "o1-mini",
        "o1",
        "o3-mini",
        "gpt-4o-mini",
        "o3",
        "o4-mini",
    }:
        return OpenAIBatchRequestModel(**model_config)
    elif model_type == "vllm":
        num_gpu = torch.cuda.device_count()
        model_config["tensor_parallel_size"] = num_gpu
        return VLLMBatchInferenceModel(**model_config)


def default_chat_template_func(x):
    ret = ""
    for utt in x:
        ret += f"{utt['role']}: {utt['content']}\n"
    return ret


def build_tokenizer(model_config: dict):

    model_name = model_config["name"]
    model_type = model_config.get("type", "vllm")
    if model_name in {
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-4.1-nano",
        "gpt-4o",
        "o1-mini",
        "o1",
        "o3-mini",
        "gpt-4o-mini",
        "o3",
        "o4-mini",
    }:
        try:
            enc = tiktoken.encoding_for_model(model_name)
        except:
            enc = tiktoken.get_encoding("o200k_base")
        return lambda x: enc.encode(x), lambda x: x
    if model_type == "deepseek":
        if model_name == "deepseek-chat":
            tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-V3")
        elif model_name == "deepseek-reasoning":
            tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-R1")
        if hasattr(tokenizer, "apply_chat_template"):
            return lambda x: tokenizer.tokenize(
                x
            ), lambda x: tokenizer.apply_chat_template(
                x, tokenize=False, add_generation_prompt=True
            )
        else:
            print("default tokenizer")
            return lambda x: tokenizer.tokenize(x), lambda x: default_chat_template_func
    elif model_type == "openrouter":
        if model_name in {
            "microsoft/mai-ds-r1:free",
            "qwen/qwen3-8b",
            "qwen/qwen3-32b",
        }:
            if model_name == "microsoft/mai-ds-r1:free":
                tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-R1")
            else:
                tokenizer = AutoTokenizer.from_pretrained(model_name)
            if hasattr(tokenizer, "apply_chat_template"):
                if (
                    model_name.find("qwen3") != -1
                    and model_config.get("enable_thinking", False) == False
                ):
                    return lambda x: tokenizer.tokenize(
                        x
                    ), lambda x: tokenizer.apply_chat_template(
                        x,
                        tokenize=False,
                        add_generation_prompt=True,
                        enable_thinking=False,
                    )
                else:
                    return lambda x: tokenizer.tokenize(
                        x
                    ), lambda x: tokenizer.apply_chat_template(
                        x, tokenize=False, add_generation_prompt=True
                    )
            else:
                print("default tokenizer")
                return (
                    lambda x: tokenizer.tokenize(x),
                    lambda x: default_chat_template_func,
                )

        elif model_name.find("gemini") != -1:
            return lambda x: x.split(), lambda x: x
        else:
            raise ValueError(f"Invalid model type: {model_type}")
    else:
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        if hasattr(tokenizer, "apply_chat_template"):

            if (
                model_name.startswith("Qwen/Qwen3") or model_name.find("qwen3") != -1
            ) and model_config.get("enable_thinking", False) == False:
                return lambda x: tokenizer.tokenize(
                    x
                ), lambda x: tokenizer.apply_chat_template(
                    x, tokenize=False, add_generation_prompt=True, enable_thinking=False
                )
            else:
                return lambda x: tokenizer.tokenize(
                    x
                ), lambda x: tokenizer.apply_chat_template(
                    x, tokenize=False, add_generation_prompt=True
                )
        else:
            print("default tokenizer")
            return lambda x: tokenizer.tokenize(x), lambda x: default_chat_template_func
