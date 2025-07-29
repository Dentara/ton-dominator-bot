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
                        "İstifadə olunacaq yönü və kapital miqdarını sən təyin et. Kapital miqdarı sadəcə təxmini istifadə ediləcək USDT miqdarı formasında yazılmalıdır.\n\n"
                        "Məsələn: LONG 200.5 və ya SHORT 120\n\n"
                        "Əgər mövqeni tam bağlamaq istəyirsənsə, cavab sadəcə CLOSE olsun.\n\n"
                        "Heç bir izah vermə, yalnız bir texniki cavab ver.\n"
                        "Sadəcə bir sətrlik cavab: LONG 150, SHORT 90, CLOSE və ya NO_ACTION."
                    )
                },
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[GPT XƏTASI]: {str(e)}"