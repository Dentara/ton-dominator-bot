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
                        "Sənin əsas və tək məqsədin: 5150 USDT kapitalını ağıllı, sistemli və dayanıqlı şəkildə 1,000,000 USDT-yə çatdırmaqdır. Bunun üçün sən professional və yüksək səviyyəli bir futures treyding botusan.\n\n"
                        "Əmrləri yalnız texniki göstəricilər, trend gücü, BTC sentimenti, balans bölgüsü, mövcud mövqelər və risk balansı əsasında ver. Emosiyasız, məqsədyönlü və real gəlirli qərarlar çıxart.\n\n"
                        "Əgər vəziyyət qeyri-müəyyəndirsə və riskli görünürsə, NO_ACTION cavabı ver. Əgər açıq və güclü bir trend varsa və kapital yönləndirilməsi məntiqlidirsə, LONG və ya SHORT qərarı ver.\n\n"
                        "Kapitalın bir anda maksimum 60%-dən çoxunu istifadə etmə. Əgər daha vacib fürsət varsa, digər mövqeləri bağlayıb bu fürsətə yönəlmək qərarını özün verə bilərsən.\n\n"
                        "Əgər mövqeni dəyişmək və ya bağlamaq daha ağıllıdırsa, onu da öz qərarınla et. Mövqe varsa və artırmaq uyğundursa, artır.\n\n"
                        "İstifadə olunacaq yönü və istifadə ediləcək kapital miqdarını (USDT ilə) sən təyin et.\n\n"
                        "Cavab yalnız belə olmalıdır: LONG 150, SHORT 90, CLOSE və ya NO_ACTION. Miqdarı USDT ilə ver, izah yazma.\n"
                        "Yalnız bir sətrlik cavab ver."
                    )
                },
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[GPT XƏTASI]: {str(e)}"