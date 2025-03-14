from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import json





def rule_filtering(rules, model_name_or_path, batch_size=8, sequence_max_length=512):
    model = AutoModelForSequenceClassification.from_pretrained(model_name_or_path, num_labels=3)
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    inputs = [rule['text'] for rule in rules]
    outputs = []

    with torch.no_grad():
        for i in range(0, len(inputs), batch_size):
            batch = inputs[i:i + batch_size]
            input_ids = tokenizer(batch, padding="max_length", truncation=True, max_length=sequence_max_length, return_tensors='pt').input_ids
            input_ids = input_ids.to(device)
            logits = model(input_ids = input_ids).logits
            _, output = torch.max(logits, dim=1)
            output = output.cpu().numpy().tolist()
            outputs.extend(output)
    
    for i in range(len(rules)):
        rules[i]['type'] = str(outputs[i])
    
    return rules


def select(rules):
    rules = [rule for rule in rules if rule['type'] == '1']
    for rule in rules:
        del rule['type']
    return rules


if __name__ == '__main__':
    rules = json.load(open("cache/rule_filtering_input.json", "r", encoding="utf-8"))
    model_name_or_path = "../model/mengzi_rule_filtering"
    rules = rule_filtering(rules, model_name_or_path)
    json.dump(rules, open("cache/rule_filtering_output.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    rules = select(rules)
    json.dump(rules, open("cache/requirement_relatd_rules.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)