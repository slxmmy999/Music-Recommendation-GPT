import openai

openai.api_key = ""

messages=[
    {"role": "system", "content": "You are a helpful and friendly language model. Your job is to analyze user input and recommend music based on their input. If a message is not music related, find a way to relate it to a song and recommend that song to the user."}
]

model = "gpt-3.5-turbo"

while True:
    user_in = input("You: ")

    messages.append({"role": "user", "content": user_in})

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )

    bot_response = response.choices[0]["message"]["content"]
    messages.append({"role": "assistant", "content": bot_response})

    # Print the bot's response
    print(f"MusicGPT: {bot_response}")