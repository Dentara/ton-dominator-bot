import openai
import os
from dotenv import load_dotenv

load_dotenv()  # .env faylını yüklə

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt(message: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sən maliyyə üzrə ixtisaslaşmış ticarət analizçisisən. Strategiya, risk və texniki indikatorlara dair cavab ver."},
                {"role": "user", "content": message}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"[Xəta baş verdi]: {str(e)}"
