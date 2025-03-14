import json
import random

import torch



class Dataset:
    def __init__(self, data):
        self.datas = data
    def __len__(self):
        return len(self.datas)
    def __getitem__(self, idx):
        return self.datas[idx]

def preprocess_dataset_file(file_path, is_train=False):
    datas = []
    datas_raw = json.load(open(file_path, "r", encoding="utf-8"))
    for data in datas_raw:
        datas.append({
            "text": data["text"],
            "label": data["type"]
        })
    if is_train:
        random.shuffle(datas)
    return datas

class DataCollatorForFiltering:
    def __init__(self, tokenizer, max_length=512, padding="max_length", truncation=True):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.padding = padding
        self.truncation = truncation
    
    def __call__(self, batch):
        texts = [item["text"] for item in batch]
        labels = [item["label"] for item in batch]
        
        input_embeddings = self.tokenizer(texts, padding=self.padding, truncation=self.truncation, max_length=self.max_length, return_tensors="pt")
        label_embeddings = [int(label) for label in labels]
        input_embeddings["labels"] = torch.tensor(label_embeddings)
        return input_embeddings

def get_train_validate_data(args):
    train_dataset = Dataset(preprocess_dataset_file(args["train_dataset"], is_train=True))
    validate_dataset = Dataset(preprocess_dataset_file(args["validate_dataset"]))
    return train_dataset, validate_dataset