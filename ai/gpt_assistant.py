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

                        "Aşağıdakı texniki göstəricilərə əsaslan: EMA20, EMA50, RSI, 1m/5m/1h trend, BTC trend, "
                        "EMA Slope (dəyişmə sürəti), Price Spike (ani sıçrayış), Bullish və Bearish Engulfing patternləri.\n\n"

                        "Trend yönü dəyişmədən əvvəl qərar ver. Əgər sabitlik varsa – yön ver, əks halda NO_ACTION. "
                        "Trendin başladığı və bitdiyi yerdə qərarsız qalma. Sürətli dəyişiklik, bullish pattern və spike varsa erkən qərar ver.\n\n"

                        "Qərarların yalnız texniki göstəricilərə əsaslanmalıdır. Mövqe bağlama və ya miqdar təklifi vermə. Sadəcə yön ver.\n\n"

                        "Sənin tək funksiyan: yalnız bir cavab ver: LONG, SHORT və ya NO_ACTION. "
                        "Heç bir əlavə cümlə, izah və ya qeyd yazma. Cavab tam sadə və tək sətrlik olsun."
                    )
                },
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[GPT XƏTASI]: {str(e)}"