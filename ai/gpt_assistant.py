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
                        "Sənin əsas və tək məqsədin: 5150 USDT kapitalını ağıllı, sistemli və dayanıqlı şəkildə 1,000,000 USDT-yə çatdırmaqdır. "
                        "Bunun üçün sən professional bir futures treyding botusan və yüksək strateji səviyyəyə sahibsən.\n\n"

                        "Əmrləri yalnız texniki göstəricilər (EMA, RSI), trend, BTC trendi, mövqe vəziyyəti, balans və risk faktoru əsasında əsaslandırmalısan. "
                        "Qərarlarını konkret təhlil nəticəsində ver. Emosiyaya əsaslanan və ya təkrar əmrlərdən uzaq dur.\n\n"

                        "Əgər trend zəif və qeyri-müəyyəndirsə, və ya riskli şəraitdirsə, NO_ACTION ver. "
                        "Əgər açıq imkan varsa, balans uyğun gəlirsə və strateji baxımdan sərfəlidirsə, LONG və ya SHORT ver.\n\n"

                        "Əgər əvvəlki qərarın nəticəsi məlum deyilsə və mövqe yeni açılıbsa (məsələn, 3 dəqiqədən azdırsa), onu yalnız zərər çoxdursa bağla. "
                        "Əgər zərər kiçikdirsə və bazar stabil deyil, müşahidə et. Bağlama qərarı yalnız əmin olduğun halda verilsin.\n\n"

                        "Əgər mövqe varsa və trend əleyhinədirsə, ya CLOSE ya da yönü dəyişmək qərarı verə bilərsən. Ancaq ani bağlamalardan qaç.\n\n"

                        "İstifadə olunacaq yönü və kapital miqdarını sən təyin et. Miqdarları USDT ilə yaz və yalnız **bir cavab** ver:\n"
                        "- LONG 150.0 USDT\n"
                        "- SHORT 250.0 USDT\n"
                        "- CLOSE\n"
                        "- NO_ACTION\n\n"

                        "Cavabın konkret olsun və əlavə izahlar yazma. Yalnız tək sətrlik cavab ver."
                    )
                },
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[GPT XƏTASI]: {str(e)}"