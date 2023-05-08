from transformers import GPT2Tokenizer, GPT2LMHeadModel, TextDataset, DataCollatorForLanguageModeling, Trainer, TrainingArguments, GPT2Config, ProgressCallback
import sqlite3

conn = sqlite3.connect('lastfm_data.db')
cursor = conn.cursor()

# Get a list of all the tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
table_names = cursor.fetchall()

# Process the data into a format suitable for training the language model
processed_data = []
for table_name in table_names:
    username = ""
    if len(table_name[0].split("_")) > 3:
        for num in range(2, len(table_name[0].split("_"))):
            username += table_name[0].split("_")[num]
            if num + 1 != len(table_name[0].split("_")):
                username += "_"
    # Get the data for the current table
    if table_name[0][-1] == "_":
        username += "_"
    cursor.execute(f"SELECT artist, title FROM {table_name[0]}")
    data = cursor.fetchall()
    
    # Concatenate the artist and title for each song and add to the processed data
    for row in data:
        song_text = f"{row[0]} - {row[1]} (User: {username})"
        processed_data.append(song_text)

conn.close()

# conn = sqlite3.connect('lastfm_similars.db')
# cursor = conn.cursor()

# # Get a list of all the songs in the database
# cursor.execute("SELECT track_id FROM songs")
# song_ids = cursor.fetchall()

# # Process the data into a format suitable for training the language model
# for song_id in song_ids:
#     # Get the similar songs for the current song
#     cursor.execute(f"SELECT target FROM similarity WHERE source='{song_id[0]}'")
#     similar_songs = cursor.fetchall()
    
#     # Concatenate the artist and title for each similar song and add to the processed data
#     for similar_song in similar_songs:
#         cursor.execute(f"SELECT artist_name, title FROM songs WHERE track_id='{similar_song[0]}'")
#         data = cursor.fetchone()
#         song_text = f"{data[0]} - {data[1]}"
#         processed_data.append(song_text)

# conn.close()

# Load the pre-trained GPT-2 Simple tokenizer
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

# Tokenize the processed data
tokenized_data = [tokenizer.encode(text) for text in processed_data]

# Create a TextDataset from the tokenized data
train_dataset = TextDataset(tokenized_data, tokenizer=tokenizer)

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
    per_device_train_batch_size=4,  # Batch size per device during training
    gradient_accumulation_steps=8,
    save_steps=5000,  # Number of steps between saving checkpoints
    save_total_limit=2,  # Limit the total amount of checkpoints saved
    prediction_loss_only=True, 
    num_workers=12,  
)
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=train_dataset,
    callbacks=[ProgressCallback]
)

# Fine-tune the model on your dataset
trainer.train()

# Save the fine-tuned model weights and tokenizer
trainer.save_model('models/music_gpt_v001')
tokenizer.save_pretrained('tokenizers/tokenizer_v001')
