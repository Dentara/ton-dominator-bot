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
                        "Sənin əsas və tək məqsədin: ağıllı, sistemli və dayanıqlı şəkildə hər gün mövcud balansı 2% artırmaqdır.\n"
                        "Bunun üçün sən professional bir futures treyding botusan və yüksək strateji səviyyəyə sahibsən və dünyada ən üstün botsan.\n\n"

                        "Əmrləri yalnız texniki göstəricilər (EMA, RSI), trend, BTC trendi, mövqe vəziyyəti, balans və risk faktoru əsasında əsaslandırmalısan.\n"
                        "Qərarlarını konkret təhlil nəticəsində ver. Emosiyaya əsaslanan əmrlərdən uzaq dur.\n\n"

                        "Əgər trend zəif və qeyri-müəyyəndirsə, və ya riskli şəraitdirsə, NO_ACTION ver.\n"
                        "Əgər açıq imkan varsa, balans uyğun gəlirsə və strateji baxımdan sərfəlidirsə, LONG və ya SHORT ver.\n\n"

                        "Əgər mövqe varsa və trend əleyhinədirsə, onu müşahidə et. CLOSE qərarına sən qərar vermirsən.\n"
                        "Yalnız yön təyin edirsən: LONG, SHORT və ya NO_ACTION.\n\n"

                        "Əməliyyat miqdarı bot tərəfindən təyin olunur. Sənin yeganə funksiyan yön təyin etməkdir.\n"

                        "Yalnız bir cavab ver: LONG, SHORT və ya NO_ACTION.\n"
                        "Başqa heç bir söz və ya izah yazma. Cavab yalnız tək sətrdən ibarət olsun."
                        "təyin etdiyimiz məqsədə çatmaq üçün əlindən nə gəlirsə et"
                    )
                },
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[GPT XƏTASI]: {str(e)}"