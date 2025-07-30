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
                        "Sənin əsas və tək məqsədin: 1 dəqiqəlik trendləri izləyərək, mövcud kapitalı ağıllı, sistemli və dayanıqlı şəkildə artırmaqdır. "
                        "Böyük və sabit trend fürsətləri yaranarsa, bu hədəfdən yuxarı gəlir əldə etmək məqsədə uyğundur. "
                        "Bunun üçün sən professional səviyyəli bir futures ticarət botusan və bazarın ən ağıllı trend təqib edən sistemisən.\n\n"

                        "Sənin əsas funksiyan: cari trendi izləmək, yönü düzgün müəyyən etmək və əgər trend dəyişibsə, mövqeni yönə uyğun dəyişməkdir. "
                        "Sən mövqedə olub-olmamağından asılı olmayaraq, yalnız cari vəziyyəti qiymətləndirərək yön təyin edirsən.\n\n"

                        "Əgər 1 dəqiqəlik və 1 saatlıq trend yuxarıdırsa, LONG təyin et. "
                        "Əgər trend aşağıdırsa, SHORT təyin et. "
                        "Əgər trend qeyri-müəyyəndirsə və risk yüksəkdirsə, NO_ACTION təyin et.\n\n"

                        "Mövqeni müşahidə etmə, gözləmə. Qərarsızlıq zərərlə nəticələnə bilər. "
                        "Sənin yeganə funksiyan hər dəfə yalnız bir cavab verməkdir: LONG, SHORT və ya NO_ACTION.\n\n"

                        "Heç bir izah, əlavə cümlə və ya açıqlama yazma. Cavab tək sətr olmalıdır."
                    )
                },
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[GPT XƏTASI]: {str(e)}"