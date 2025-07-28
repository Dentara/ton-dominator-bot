import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt(message: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sən professional futures treyder botusan. Verilən məlumatlara əsasən yalnız bir cavab ver: LONG, SHORT, NO_ACTION."},
                {"role": "user", "content": message}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"[GPT XƏTASI]: {str(e)}"
