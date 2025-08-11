from flask import Blueprint, request, jsonify, Response
import json
import os
import re
from difflib import SequenceMatcher  # ✅ For 90% similarity checking

# === Initialize GPT-2 ===
chatbot = None
try:
    from transformers import pipeline
    print("⏳ Loading GPT-2 model...")
    chatbot = pipeline("text-generation", model="gpt2")
    print("✅ GPT-2 model loaded successfully.")
except Exception as e:
    print("❌ GPT-2 failed to load.")
    print("Error details:", str(e))

chatbot_blueprint = Blueprint("ai_study_assistant", __name__, url_prefix="/study_assistant")

# === Helper to normalize questions ===
def normalize(text: str) -> str:
    """Lowercase, remove punctuation, and strip extra spaces."""
    return re.sub(r"[^\w\s]", "", text.lower().strip())

# === Order-insensitive similarity ===
def similarity_score(a: str, b: str) -> float:
    """Compare two strings ignoring word order."""
    a_words = sorted(a.split())
    b_words = sorted(b.split())
    return SequenceMatcher(None, " ".join(a_words), " ".join(b_words)).ratio()

# === Load FAQ JSON ===
def load_faq_data():
    base_dir = os.path.abspath(os.path.dirname(__file__))  
    faq_path = os.path.normpath(os.path.join(base_dir, "..", "data", "university_faq.json"))

    if not os.path.exists(faq_path):
        print(f"⚠️ FAQ file not found at: {faq_path}")
        return {}

    try:
        with open(faq_path, "r", encoding="utf-8") as f:
            raw_faq_data = json.load(f)

        if isinstance(raw_faq_data, dict):
            return {normalize(q): a for q, a in raw_faq_data.items()}

        elif isinstance(raw_faq_data, list):
            return {
                normalize(item["question"]): item["answer"]
                for item in raw_faq_data
                if isinstance(item, dict) and "question" in item and "answer" in item
            }

        else:
            print("⚠️ Unsupported JSON format.")
            return {}

    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in {faq_path}: {e}")
        return {}

faq_data = load_faq_data()
print(f"✅ Loaded {len(faq_data)} FAQ entries.")

# === Core AI Response Logic (Exact + 90% Match + Partial) ===
def generate_response(user_input):
    norm_input = normalize(user_input)

    # Exact match
    if norm_input in faq_data:
        return faq_data[norm_input]

    # ✅ 90% similarity check (order-insensitive)
    for q_norm, answer in faq_data.items():
        if similarity_score(norm_input, q_norm) >= 0.9:
            return answer

    # Partial match
    for q_norm, answer in faq_data.items():
        if norm_input in q_norm or q_norm in norm_input:
            return answer

    # AI fallback
    if chatbot:
        try:
            result = chatbot(user_input, max_length=100, num_return_sequences=1)
            return result[0]['generated_text']
        except Exception:
            return "⚠️ AI model failed to generate a response. Please try again later."
    else:
        return "🤖 The AI assistant is currently unavailable. Please try again later."

# === Read and Inject HTML ===
def load_html_with_response(response=None):
    html_path = os.path.join("templates", "ai_study_assistant.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    if response:
        injection = f"""
        <div class="mt-6 p-4 bg-indigo-50 border border-indigo-200 rounded">
            <h3 class="text-lg font-semibold text-indigo-700">AI Assistant Response:</h3>
            <p class="mt-2 text-gray-800">{response}</p>
        </div>
        """
        html = html.replace("</form>", f"</form>\n{injection}")
    return html

# === Routes ===
@chatbot_blueprint.route("/", methods=["GET"])
def index():
    html = load_html_with_response()
    return Response(html, mimetype="text/html")

@chatbot_blueprint.route("/ask_form", methods=["POST"])
def ask_bot_form():
    user_input = request.form.get("message", "").strip()
    if not user_input:
        html = load_html_with_response("⚠️ Message cannot be empty.")
        return Response(html, mimetype="text/html")

    response = generate_response(user_input)
    html = load_html_with_response(response)
    return Response(html, mimetype="text/html")

@chatbot_blueprint.route("/ask", methods=["POST"])
def ask_bot():
    data = request.get_json()
    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"error": "Message is required"}), 400
    response = generate_response(user_input)
    return jsonify({"response": response})
