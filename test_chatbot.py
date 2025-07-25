# test_chatbot.py
from chatbot import ask_bot

print("Type 'exit' to quit\n")
while True:
    msg = input("You: ")
    if msg.lower() == "exit":
        break
    reply = ask_bot(msg)
    print("Bot:", reply)
