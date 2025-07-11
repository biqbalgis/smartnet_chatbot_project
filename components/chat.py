from models.gemini_model import model
from components.rag import retrieve_faq_context
import difflib

# Keywords to detect if the bot just asked something and is expecting a reply
FOLLOW_UP_KEYWORDS = [
    "what were the results",
    "did you check",
    "have you checked",
    "can you confirm",
    "please tell me",
    "let me know"
]

def answer_user_query(query: str, chat_history: list) -> str:
    context = retrieve_faq_context(query)

    system_prompt = (
        "You are SmartNet ISP support bot. "
        "If the user already asked the same thing, do not repeat. "
        "If you asked a question and the user hasn’t answered it, remind them to answer before giving new steps."
    )

    messages = [{"role": "user", "parts": [system_prompt]}]

    for turn in chat_history:
        messages.append({"role": "user", "parts": [turn["user"]]})
        messages.append({"role": "model", "parts": [turn["bot"]]})

    # Get context + new query
    formatted_context = "\n".join(context)
    user_prompt = (
        f"Context:\n{formatted_context}\n\n"
        f"User says:\n{query}\n\n"
        "Reminder: Do not repeat troubleshooting. If you're waiting for an answer to a previous question, ask again."
    )
    messages.append({"role": "user", "parts": [user_prompt]})

    try:
        response = model.generate_content(messages)
        new_reply = response.text.strip()

        # 🔁 Similarity check
        recent_replies = [turn["bot"] for turn in chat_history[-4:] if "bot" in turn]
        for prev in recent_replies:
            if difflib.SequenceMatcher(None, prev, new_reply).ratio() > 0.9:
                return (
                    "🔁 We've already gone over those steps. Please answer the last question so I can assist further."
                )

        # ⏸️ Check if bot asked a follow-up last time, and user didn't answer
        if chat_history:
            last_bot = chat_history[-1]["bot"].lower()
            last_user = chat_history[-1]["user"].lower()
            if any(kw in last_bot for kw in FOLLOW_UP_KEYWORDS) and last_user == query.lower():
                return "🔄 Please answer my previous question so I can continue helping you."

        return new_reply

    except Exception as e:
        return f"❌ Gemini Error: {str(e)}"





