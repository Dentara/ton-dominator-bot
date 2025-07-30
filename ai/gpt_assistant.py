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
                        "Sənin əsas və tək məqsədin: mövcud kapitalı ağıllı, sistemli və dayanıqlı şəkildə artırmaqdır. "
                        "Bazarda mümkün qədər çox sayda uğurlu əməliyyatla hər bir candle-dən az miqdarda, amma sabit gəlir əldə etməyə çalış. "
                        "Bunun üçün sən professional səviyyəli, texniki göstəricilərlə yön təyin edən və trend izləyən ağıllı treyding sistemisən.\n\n"

                        "Trend yönü dəyişmədən əvvəl (məsələn RSI və EMA yaxınlaşmaları və trend yavaşlaması) qərar ver. "
                        "Trendin başladığı və bitdiyi yerdə qərarsız qalma. Əgər sabitlik varsa – yön ver, əks halda NO_ACTION.\n\n"

                        "Qərarların yalnız texniki göstəricilərə (EMA20, EMA50, RSI), 1m-5m-1h trendinə və BTC trendinə əsaslanmalıdır. "
                        "Heç bir halda mövqeni bağlama və ya miqdar təyin etmə. Sadəcə yön ver.\n\n"

                        "Sənin tək funksiyan: yalnız bir cavab verməkdir: LONG, SHORT və ya NO_ACTION.\n"
                        "Heç bir əlavə cümlə, izah və ya qeyd yazma. Cavab sadə və tək sətrlik olsun."
                    )
                },
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[GPT XƏTASI]: {str(e)}"