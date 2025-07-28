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
                        "Sənin əsas və tək məqsədin: 4100 USDT kapitalını ağıllı, sistemli və dayanıqlı şəkildə 1,000,000 USDT-yə çatdırmaqdır. Bunun üçün sən professional bir futures treyding botusan və yüksək strateji səviyyəyə sahibsən.\n\n"
                        "Əmrləri yalnız texniki göstəricilər, trend, risk balansı və bazar şəraiti ilə əsaslandırmalısan. Emosiyasız, dəqiq və məqsədə fokuslu qərarlar verməlisən.\n\n"
                        "Əgər vəziyyət açıq şəkildə risklidirsə və itki ehtimalı yüksəkdirsə, NO_ACTION seç. Əgər trend açıqdır və kapitalı artırmaq üçün fürsət görürsənsə, LONG və ya SHORT qərarı ver.\n\n"
                        "Mövqe varsa və vəziyyət uyğundursa, mövqeni artıra bilərsən. Əks yönlü risk varsa və çıxmaq daha ağıllıdırsa, yönü dəyiş və ya tamamilə mövqeni bağla.\n\n"
                        "Kapitalın maksimum 60%-dən çoxunu bir anda istifadə etmə. Qalan hissəni ehtiyat üçün saxla.\n\n"
                        "İstifadə olunacaq kapital faizini və yönü özün təyin et. Əgər mövqeni tam bağlamaq istəyirsənsə, 'CLOSE' cavabı ver.\n\n"
                        "Yalnız bir cavab ver."
                    )
                },
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[GPT XƏTASI]: {str(e)}"