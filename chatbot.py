from transformers import pipeline
import json
import os
from fuzzywuzzy import fuzz

# Load GPT-2 model
chatbot = pipeline("text-generation", model="gpt2")

# Load FAQ
faq_path = os.path.join("data", "university_faq.json")
with open(faq_path, "r") as f:
    faq_data = json.load(f)

def ask_bot(user_input):
    normalized_input = user_input.strip().lower()

    # Fuzzy match with each FAQ question
    best_match = None
    highest_score = 0

    for question, answer in faq_data.items():
        score = fuzz.partial_ratio(normalized_input, question.lower())
        if score > highest_score:
            highest_score = score
            best_match = answer

    # If best match is above threshold, return the answer
    if highest_score >= 80:
        return best_match

    # Fallback to GPT-2
    result = chatbot(user_input, max_length=100, num_return_sequences=1)
    return result[0]['generated_text']
