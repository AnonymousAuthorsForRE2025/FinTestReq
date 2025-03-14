from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
from train_llm.arguments import arg_parser
from train_llm.data_loader import get_train_validate_data, DataCollatorForFiltering
import torch
import time


def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda:0")
    return torch.device("cpu")

def get_training_arguments(args):
    training_args = TrainingArguments(
        num_train_epochs=args["num_train_epochs"],
        per_device_train_batch_size=args["per_device_train_batch_size"],
        per_device_eval_batch_size=args["per_device_eval_batch_size"],
        logging_steps=args["logging_step"],
        evaluation_strategy=args["evaluation_strategy"],
        eval_steps=args["eval_steps"],
        load_best_model_at_end=args["load_best_model_at_end"],
        learning_rate=args["learning_rate"],
        output_dir=args["output_dir"],
        save_total_limit=args["save_total_limit"],
        lr_scheduler_type=args["lr_scheduler_type"],
        gradient_accumulation_steps=args["gradient_accumulation_steps"],
        dataloader_num_workers=args["dataloader_num_workers"],
        remove_unused_columns=args["remove_unused_columns"],
        logging_dir=args["logging_dir"],
        save_strategy=args["save_strategy"],
        save_steps=args["save_steps"],
        disable_tqdm=args["disable_tqdm"],
        weight_decay=args["weight_decay"],
    )
    return training_args


def get_model_and_tokenizer(args):
    model = AutoModelForSequenceClassification.from_pretrained(args["base_model"], num_labels=3)
    tokenizer = AutoTokenizer.from_pretrained(args["base_model"])
    return model, tokenizer


def train(args):
    device = get_device()
    model, tokenizer = get_model_and_tokenizer(args)
    model.to(device)
    train_dataset, validate_dataset = get_train_validate_data(args)
    data_collator = DataCollatorForFiltering(tokenizer, max_length=args["sentence_max_length"], padding="max_length", truncation=True)
    training_args = get_training_arguments(args)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=validate_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer
    )

    start = time.time()
    trainer.train()
    print(f"Training time: {time.time() - start}")
    trainer.save_model(args["output_dir"] + f"/mengzi_rule_filtering_{int(time.time())}")
    print("Model saved at", args["output_dir"] + f"/mengzi_rule_filtering_{int(time.time())}")


if __name__ == "__main__":
    args = arg_parser()
    train(args)