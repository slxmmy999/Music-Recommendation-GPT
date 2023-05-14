from transformers import GPT2Tokenizer, GPT2LMHeadModel, TextDataset, DataCollatorForLanguageModeling, Trainer, TrainingArguments, GPT2Config, ProgressCallback
from torch.utils.data import IterableDataset, DataLoader, ConcatDataset
import os

class TextIterableDataset(IterableDataset):
    def __init__(self, dataset):
        self.dataset = dataset

    def __iter__(self):
        for i in range(len(self.dataset)):
            yield self.dataset[i]

def data_loader(batch_size=4):
    return DataLoader(TextIterableDataset(train_dataset), batch_size=batch_size)

# Load the pre-trained GPT-2 Simple tokenizer
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

# Create a TextDataset from the tokenized data
files_dir = "./dataset"
files = os.listdir(files_dir)

datasets = []
for file in files:
    if file.endswith(".txt") and file.startswith("tokenized"):
        file_path = os.path.join(files_dir, file)
        dataset = TextDataset(
            file_path=file_path,
            tokenizer=tokenizer,
            block_size=128
        )
        datasets.append(dataset)

train_dataset = ConcatDataset(datasets)

# Load the pre-trained GPT-2 Simple model configuration
model_config = GPT2Config.from_pretrained('gpt2')

# Load the pre-trained GPT-2 Simple model weights
model = GPT2LMHeadModel.from_pretrained('gpt2', config=model_config)

# Use the DataCollatorForLanguageModeling to batch and pad the dataset
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=False
)

# Set up the Trainer with the TrainingArguments
training_args = TrainingArguments(
    output_dir='./results',  # The output directory
    num_train_epochs=1,  # Total number of training epochs
    per_device_train_batch_size=16,  # Batch size per device during training
    gradient_accumulation_steps=2,
    save_steps=5000,  # Number of steps between saving checkpoints
    save_total_limit=2,  # Limit the total amount of checkpoints saved
    prediction_loss_only=True 
)
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=train_dataset,
    callbacks=[ProgressCallback]
)

# Fine-tune the model on your dataset
print("beginning training")
trainer.train()

# Save the fine-tuned model weights and tokenizer
trainer.save_model('models/music_gpt_v001')
tokenizer.save_pretrained('tokenizers/tokenizer_v001')