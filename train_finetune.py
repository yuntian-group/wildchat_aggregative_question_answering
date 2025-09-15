import os
import yaml
import wandb
import argparse
import datasets
from accelerate import Accelerator
from yaml import CLoader as Loader
from utils.utils import seed_everthing
from utils.logging_utils import init_logger
from dataloader.wildchat_aqa_dataset import WildChatAQACollator, WildChatAQADataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model

PROJECT_NAME = "wildchat-AQA-finetune"


def main(args):
    accelerator = Accelerator(log_with="wandb")
    seed_everthing(args.seed)
    log_path, logger = init_logger(args.config_path)
    with open(args.config_path, "r") as f:
        config = yaml.load(f, Loader=Loader)
    if accelerator.is_main_process:
        os.environ["WANDB_DIR"] = log_path
        wandb.init(
            project=PROJECT_NAME,
            config={**config["train"], **config["data"]["train"]},
            mode="online" if args.wandb else "disabled",
        )
    model_config = config["model"]
    train_config = config["train"]
    data_config = config["data"]
    bnb_config = config.get("bnb_config", {})
    peft_config = config.get("peft_config", {})

    train_config["output_dir"] = log_path

    use_bnb = bnb_config.pop("use_bnb", False)
    if use_bnb:
        bnb_config = BitsAndBytesConfig(**bnb_config)
    else:
        bnb_config = None

    model = AutoModelForCausalLM.from_pretrained(
        model_config["model_name"],
        # attn_implementation=model_config["attn_implementation"],
        # quantization_config=bnb_config,
        # device_map="auto",
    )
    tokenizer = AutoTokenizer.from_pretrained(
        model_config["model_name"], padding_side="left"
    )
    tokenizer.pad_token = tokenizer.eos_token
    collator = WildChatAQACollator(tokenizer)

    use_peft = peft_config.pop("use_peft", False)
    if use_peft:
        peft_config = LoraConfig(**peft_config)
        model = get_peft_model(model, peft_config)
    logger.info("Loading data")

    train_data = WildChatAQADataset(
        data_path=data_config["train"]["data_path"],
        tokenizer=tokenizer,
        summary=data_config["train"].get("summary", False),
    )
    logger.info("Start training")

    train_args = Seq2SeqTrainingArguments(**train_config)

    trainer = Seq2SeqTrainer(
        model=model,
        args=train_args,
        train_dataset=train_data,
        data_collator=collator,
    )
    trainer.train(args.resume_from_checkpoint)
    trainer.save_model()
    accelerator.end_training()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config_path",
        type=str,
        default="configs/wildchat_aqa/train/qwen3_8b_train.yaml",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--wandb", action="store_true")
    parser.add_argument("--resume_from_checkpoint", type=str, default=None)
    args = parser.parse_args()
    datasets.disable_caching()
    main(args)
