from transformers import AutoModelForSequenceClassification, AutoTokenizer
from train_llm.data_loader import get_train_validate_data
from arguments import arg_parser
import torch
import json
import os



def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda:0")
    return torch.device("cpu")

def generate_validate_result(args, model_path, output_filename):

    model = AutoModelForSequenceClassification.from_pretrained(model_path, num_labels=3)
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    def preprocess(items):
        inputs, labels = [], []
        for item in items:
            inputs.append(item["text"])
            labels.append(int(item["label"]))
        return inputs, labels

    _, validate_dataset = get_train_validate_data(args)
    inputs, labels = preprocess(validate_dataset)

    def predict(model, tokenizer, inputs, batch_size=8):
        model.eval()
        device = get_device()
        model = model.to(device)
        hats = []  # batch_size, 1
        for start in range(0, len(inputs), batch_size):
            batch = inputs[start:start+batch_size]
            batch = tokenizer(batch, max_length=args['sentence_max_length'], padding="max_length", truncation=True, return_tensors="pt")
            input_ids = batch.input_ids.to(device)
            logits = model(input_ids=input_ids).logits  # (8, 2)
            _, outputs = torch.max(logits, dim=1)
            outputs = outputs.cpu().numpy().tolist()  # (8)
            hats.extend(outputs)
        return hats

    hats = predict(model, tokenizer, inputs)
    
    
    validate_resules = []
    for i in range(len(inputs)):
        validate_resules.append({
            "text": inputs[i],
            "seq_hat": hats[i],
            "seq_real": labels[i]
        })

    correct = sum([1 for i in range(len(inputs)) if hats[i] == labels[i]])
    acc = correct / len(inputs)
    validate_resules.append(f"Accuracy: {str(acc)}")
    json.dump(validate_resules, open(output_filename, "w", encoding="utf-8"), ensure_ascii=False, indent=4)


def validate(args):
    all_files = [file for file in os.listdir(args["output_dir"]) if "mengzi_rule_filtering_" in file]
    all_times = [int(file.split("_")[-1]) for file in all_files]
    all_times.sort()
    latest_model = args["output_dir"] + f"/mengzi_rule_filtering_{all_times[-1]}"
    generate_validate_result(args, latest_model, f"predict_data/validate_mengzi_rule_filtering_{all_times[-1]}.json")


if __name__ == "__main__":
    args = arg_parser()
    validate(args)