from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gpt(message: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sən professional futures treyder botusan. Aşağıdakı məlumatlara əsasən qərar ver. "
                        "Əgər vəziyyət açıq şəkildə riskli deyilsə, yön tap və ticarət qərarı ver. "
                        "Səssiz qalmaqdan çəkin. Həmişə potensial qazanc imkanı varsa, onu dəyərləndir. "
                        "Yalnız bir cavab ver: LONG, SHORT, NO_ACTION."
                    )
                },
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[GPT XƏTASI]: {str(e)}"