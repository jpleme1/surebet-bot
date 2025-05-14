import os
import time
import schedule
import requests
from telegram import Bot

# Configurações
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)

SPORTS = [
    "soccer_brazil_campeonato",
    "soccer_epl",
    "soccer_spain_la_liga",
    "basketball_nba",
    "basketball_euroleague"
]

# Armazena IDs de surebets já alertadas
surebets_enviadas = set()

def obter_odds(sport):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro [{sport}]: {response.status_code}")
            return []
    except Exception as e:
        print("Erro na API:", e)
        return []

def encontrar_surebets(eventos):
    for evento in eventos:
        odds = {}
        for book in evento["bookmakers"]:
            if book["title"] in ["Betano", "Bet365"]:
                for mercado in book["markets"]:
                    if mercado["key"] == "h2h":
                        for o in mercado["outcomes"]:
                            odds[(book["title"], o["name"])] = o["price"]
        try:
            home = max(
                odds[("Betano", evento["home_team"])],
                odds[("Bet365", evento["home_team"])]
            )
            away = max(
                odds[("Betano", evento["away_team"])],
                odds[("Bet365", evento["away_team"])]
            )
            if (1/home + 1/away) < 1:
                id_evento = f"{evento['home_team']} vs {evento['away_team']}"

                if id_evento not in surebets_enviadas:
                    surebets_enviadas.add(id_evento)
                    msg = (
                        f"Surebet encontrada!\n"
                        f"{evento['home_team']} vs {evento['away_team']}\n"
                        f"Betano: {odds.get(('Betano', evento['home_team']))} / {odds.get(('Betano', evento['away_team']))}\n"
                        f"Bet365: {odds.get(('Bet365', evento['home_team']))} / {odds.get(('Bet365', evento['away_team']))}"
                    )
                    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
        except Exception:
            continue

def tarefa():
    for sport in SPORTS:
        eventos = obter_odds(sport)
        encontrar_surebets(eventos)

def main():
    schedule.every(2).minutes.do(tarefa)
    tarefa()
    while True:
        schedule.run_pending()
        time.sleep(1)

if _name_ == "_main_":
    main()