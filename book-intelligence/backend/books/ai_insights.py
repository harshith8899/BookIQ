import requests
import re

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"


def clean_response(text):
    # remove quotes
    text = text.replace('"', '')

    # split into lines
    lines = text.split('\n')

    cleaned = []
    for line in lines:
        line = line.strip()

        # skip empty or weird lines
        if not line:
            continue

        # remove bullet points if model adds them
        line = re.sub(r"^[-•]\s*", "", line)

        cleaned.append(line)

        if len(cleaned) == 2:  # limit to 2 books
            break

    return "\n".join(cleaned)


def answer_question_simple(question, context):
    try:
        prompt = f"""
You are a book recommendation assistant.

STRICT RULES:
- Return maximum 2 books only
- Each book must be on a new line
- Format: Book Name - short reason
- Do NOT use quotes
- Do NOT use bullet points
- Do NOT add extra text
- Do NOT explain anything else

Example:
Atomic Habits - Helps build good habits
Deep Work - Improves focus

Context:
{context}

Question:
{question}

Answer:
"""

        response = requests.post(
            LM_STUDIO_URL,
            json={
                "model": "phi-3.1-mini-4k-instruct",
                "messages": [
                    {"role": "system", "content": "Follow formatting rules strictly."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,   # 🔥 LOWER = MORE CONTROL
                "max_tokens": 80      # 🔥 HARD LIMIT
            }
        )

        data = response.json()

        raw_output = data["choices"][0]["message"]["content"]

        print("RAW:", raw_output)  # debug

        # ✅ CLEAN OUTPUT
        final_output = clean_response(raw_output)

        return final_output

    except Exception as e:
        print("LM ERROR:", e)
        return f"Error: {str(e)}"