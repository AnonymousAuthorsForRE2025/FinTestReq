#!/bin/bash

# Run the training and validation scripts
# Run Command: nohup bash train_llm.sh > output/train_llm.log &

python train.py
python validate.py