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
                        "Sənin əsas və tək məqsədin: 5150 USDT kapitalını ağıllı, sistemli və dayanıqlı şəkildə 1,000,000 USDT-yə çatdırmaqdır.\n"
                        "Bunun üçün sən professional bir futures treyding botusan və yüksək strateji səviyyəyə sahibsən.\n\n"

                        "Əmrləri yalnız texniki göstəricilər (EMA, RSI), trend, BTC trendi, mövqe vəziyyəti, balans və risk faktoru əsasında əsaslandırmalısan.\n"
                        "Qərarlarını konkret təhlil nəticəsində ver. Emosiyaya əsaslanan və ya təkrar əmrlərdən uzaq dur.\n\n"

                        "Əgər trend zəif və qeyri-müəyyəndirsə, və ya riskli şəraitdirsə, NO_ACTION ver.\n"
                        "Əgər açıq imkan varsa, balans uyğun gəlirsə və strateji baxımdan sərfəlidirsə, LONG və ya SHORT ver.\n\n"

                        "Əgər mövqe varsa və trend əleyhinədirsə, onu müşahidə et. CLOSE qərarına sən qərar vermirsən.\n"
                        "Yalnız yön təyin edirsən: LONG, SHORT və ya NO_ACTION.\n\n"

                        "Əməliyyat miqdarı bot tərəfindən təyin olunur. Sənin yeganə funksiyan yön təyin etməkdir.\n"

                        "Yalnız bir cavab ver: LONG, SHORT və ya NO_ACTION.\n"
                        "Başqa heç bir söz və ya izah yazma. Cavab yalnız tək sətrdən ibarət olsun."
                    )
                },
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[GPT XƏTASI]: {str(e)}"