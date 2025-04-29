#!/bin/zsh

# Download images/JSON files:
# TODO: make python script to download Google folder
pip install gdown
mkdir /content/data/

python install_training_data.py

tar -xvzf /content/data/new_files.tar.gz -C /content/data/
find /content/data/new_files -type f -name '._*' -delete


# Clone Qwen-VL
git clone https://github.com/QwenLM/Qwen-VL.git
pip install Qwen-VL/requirements.txt

cd Qwen-VL

!torchrun --nproc_per_node 2 --nnodes 1 --node_rank 0 --master_addr localhost --master_port 6601 ../../finetune.py \
    --model_name_or_path "Qwen/Qwen2.5-VL-72B-Instruct/" \
    --data_path "path/to/our/training_data.json" \
    --bf16 True \
    --output_dir "finetuned_qwen" \
    --num_train_epochs 5 \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 16 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 1000 \
    --save_total_limit 10 \
    --learning_rate 1e-5 \
    --weight_decay 0.1 \
    --adam_beta2 0.95 \
    --warmup_ratio 0.01 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --report_to "none" \
    --model_max_length 512 \
    --gradient_checkpointing True \
    --lazy_preprocess True \
    --deepspeed "finetune/ds_config_zero2.json" \
    --use_lora \
    --q_lora

