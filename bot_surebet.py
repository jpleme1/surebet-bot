import os
import requests
import time
import telegram
from decimal import Decimal, ROUND_HALF_UP

# Tokens e chaves (use variáveis de ambiente no Render)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # você pode setar fixo ou usar seu próprio ID

bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Função para calcular surebet
def calcular_surebet(odds1, odds2):
    prob1 = 1 / odds1
    prob2 = 1 / odds2
    total_prob = prob1 + prob2
    lucro = (1 - total_prob) * 100
    return lucro if lucro > 0 else 0

# Função para buscar e comparar odds
def buscar_surebets():
    url = f"https://api.the-odds-api.com/v4/sports/?apiKey={ODDS_API_KEY}"
    response = requests.get(url)
    sports = response.json()

    for sport in sports:
        if sport['key'] not in ['soccer', 'basketball']:
            continue

        odds_url = f"https://api.the-odds-api.com/v4/sports/{sport['key']}/odds/?regions=eu&markets=h2h&oddsFormat=decimal&apiKey={ODDS_API_KEY}"
        res = requests.get(odds_url)
        if res.status_code != 200:
            continue

        data = res.json()
        for game in data:
            if len(game['bookmakers']) < 2:
                continue

            # Seleciona Betano e Bet365
            casas = {bk['title']: bk for bk in game['bookmakers'] if bk['title'] in ['Bet365', 'Betano']}
            if len(casas) < 2:
                continue

            betano_odds = casas['Betano']['markets'][0]['outcomes']
            bet365_odds = casas['Bet365']['markets'][0]['outcomes']

            for i in range(2):  # Comparar as duas odds (por ex: Time A e Time B)
                odd1 = betano_odds[i]['price']
                odd2 = bet365_odds[1 - i]['price']

                lucro = calcular_surebet(odd1, odd2)
                if lucro > 1:  # Enviar apenas se o lucro for significativo
                    mensagem = f"""
*SUREBET DETECTADA!*

Evento: {game['teams'][0]} x {game['teams'][1]}
Mercado: 1X2 (Resultado final)

Odds:
- {betano_odds[i]['name']} na *Betano*: {odd1}
- {bet365_odds[1 - i]['name']} na *Bet365*: {odd2}

Lucro garantido: {Decimal(lucro).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)}%

Aposte rápido!
"""
                    bot.send_message(chat_id=CHAT_ID, text=mensagem, parse_mode=telegram.constants.ParseMode.MARKDOWN)

# Loop principal
while True:
    try:
        buscar_surebets()
        time.sleep(60)  # Espera 60 segundos antes da próxima verificação
    except Exception as e:
        print(f"Erro: {e}")
        time.sleep(30)