import sqlite3
from transformers import GPT2Tokenizer

# Set the number of rows per file
rows_per_file = 1000

conn = sqlite3.connect('lastfm_data.db')
cursor = conn.cursor()

# Get a list of all the tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
table_names = cursor.fetchall()

# Process the data into a format suitable for training the language model
processed_data = []
count = 1
file_num = 1
file_rows = 0
for table_name in table_names:
    print(f"Writing {count} of {len(table_names)} users...")
    username = ""
    if len(table_name[0].split("_")) > 3:
        for num in range(2, len(table_name[0].split("_"))):
            username += table_name[0].split("_")[num]
            if num + 1 != len(table_name[0].split("_")):
                username += "_"
    else:
        username = table_name[0].split("_")[2]

    if table_name[0][-1] == "_":
        username += "_"

    print(username)
    # Get the data for the current table
    cursor.execute(f"SELECT artist, title FROM {table_name[0]}")
    data = cursor.fetchall()
    
    # Concatenate the artist and title for each song and add to the processed data
    for row in data:
        song_text = f"{row[0]} - {row[1]} (User: {username})"
        processed_data.append(song_text)
        file_rows += 1
        # Write the tokenized data to a file every "rows_per_file" rows
        if file_rows == rows_per_file:
            with open(f'dataset/tokenized_data_{file_num}.txt', 'a', encoding="utf-8") as f:
                for text in processed_data:
                    f.write(text + '\n')
            processed_data = []
            file_rows = 0
            file_num += 1

    count += 1

if processed_data:
    with open(f'dataset/tokenized_data_{file_num}.txt', 'a', encoding="utf-8") as f:
        for text in processed_data:
            f.write(text + '\n')

conn.close()
print(f"Finished writing to files. Total number of files: {file_num}")