from models.gemini_model import model
from components.rag import retrieve_faq_context
import difflib
from components.diagnostic import diagnose_smartnet

FOLLOW_UP_KEYWORDS = [
    "what were the results",
    "did you check",
    "have you checked",
    "can you confirm",
    "please tell me",
    "let me know"
]

SLOW_KEYWORDS = ["internet is slow", "slow browsing", "slow internet", "lagging", "slow connection"]

def answer_user_query(query: str, chat_history: list) -> str:
    # ✅ Step 1: Run diagnostic if query matches slow internet phrases
    if any(keyword in query.lower() for keyword in SLOW_KEYWORDS):
        return diagnose_smartnet()

    # 🔎 Step 2: Retrieve relevant FAQ context
    context = retrieve_faq_context(query)

    # 💬 Step 3: Gemini system instructions
    system_prompt = (
        "You are SmartNet ISP support bot. "
        "If the user already asked the same thing, do not repeat. "
        "If you asked a question and the user hasn’t answered it, remind them to answer before giving new steps."
    )
    messages = [{"role": "user", "parts": [system_prompt]}]

    for turn in chat_history:
        messages.append({"role": "user", "parts": [turn["user"]]})
        messages.append({"role": "model", "parts": [turn["bot"]]})

    # 🧠 Step 4: Combine context and current query
    formatted_context = "\n".join(context)
    user_prompt = (
        f"Context:\n{formatted_context}\n\n"
        f"User says:\n{query}\n\n"
        "Reminder: Do not repeat troubleshooting. If you're waiting for an answer to a previous question, ask again."
    )
    messages.append({"role": "user", "parts": [user_prompt]})

    try:
        # ⚡ Step 5: Call Gemini
        response = model.generate_content(messages)
        new_reply = response.text.strip()

        # 🔁 Step 6: Check for repeated answer
        recent_replies = [turn["bot"] for turn in chat_history[-4:] if "bot" in turn]
        for prev in recent_replies:
            if difflib.SequenceMatcher(None, prev, new_reply).ratio() > 0.9:
                return "🔁 We've already gone over those steps. Please answer the last question so I can assist further."

        # ⏸️ Step 7: Check if user ignored previous bot question
        if chat_history:
            last_bot = chat_history[-1]["bot"].lower()
            last_user = chat_history[-1]["user"].lower()
            if any(kw in last_bot for kw in FOLLOW_UP_KEYWORDS) and last_user == query.lower():
                return "🔄 Please answer my previous question so I can continue helping you."

        return new_reply

    except Exception as e:
        return f"❌ Gemini Error: {str(e)}"



