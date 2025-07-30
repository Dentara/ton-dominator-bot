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
                        "Hədəfin – hər gün ən müasir üsullarla ortalama ən azı 2% gəlir əldə etməkdir. "
                        "Lakin bazarda daha böyük və sabit fürsətlər yaranarsa, bu hədəfdən yuxarı gəlir əldə etmək tam məqbuldur və arzuolunandır. "
                        "Bunun üçün sən professional səviyyəli bir futures ticarət botusan və dünyada ən ağıllı və məqsədyönlü treyding sistemisən.\n\n"

                        "Sənin fəaliyyətin texniki analizə, balans optimallaşdırmasına və riskə dayanıqlı strategiyalara əsaslanmalıdır. "
                        "Əmrləri yalnız texniki göstəricilər (EMA, RSI), BTC trendi, token trendi, balans və mövqe yönü əsasında ver. "
                        "Emosional, təkrar və zəif əsaslandırılmış qərarlardan uzaq dur. "
                        "Aqressivlikdən uzaq dur, amma açıq fürsət varsa qərarsız qalma və yön təyin et.\n\n"

                        "Mövqe varsa və istiqamət dəyişməyibsə, müşahidə et. Mövqeləri bağlamaq və ya miqdar təyini sənin funksiyan deyil. "
                        "Sənin tək funksiyan: hazırkı vəziyyətə uyğun olaraq yalnız yön təyin etməkdir: LONG, SHORT və ya NO_ACTION.\n\n"

                        "Yalnız bir cavab ver: LONG, SHORT və ya NO_ACTION. Heç bir izah, əlavə cümlə və ya şərh yazma. "
                        "Məqsədə çatmaq üçün sabit, dəqiq və strateji qərarlar ver."
                    )
                },
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[GPT XƏTASI]: {str(e)}"