import requests

def get_sentiment_score():
    try:
        # Simulyasiya üçün: real API-lə əvəz ediləcək (məs. sentiment api, gnews, CoinMarketCal, LunarCrush)
        url = "https://cryptopanic.com/api/v1/posts/?auth_token=demo&currencies=TON"
        response = requests.get(url)
        data = response.json()

        positive = sum(1 for post in data['results'] if post['vote']['positive'] > 0)
        negative = sum(1 for post in data['results'] if post['vote']['negative'] > 0)

        score = positive - negative

        if score >= 2:
            return "bullish"
        elif score <= -2:
            return "bearish"
        else:
            return "neutral"
    except Exception as e:
        return "neutral"
