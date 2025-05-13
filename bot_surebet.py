
import requests
import asyncio
from telegram import Bot

API_KEY = 'cd7d10ad2ffa5ace542fc0ffa0b16c07'
TELEGRAM_TOKEN = '7162468527:AAH2dr4DE_DM0s1fL-I97GgAyNN0Uo7dzF0'
CHAT_ID = '7534646862'

bot = Bot(token=TELEGRAM_TOKEN)

ESPORTES = ['soccer', 'basketball']

def coletar_odds(api_key, esporte):
    url = f"https://api.the-odds-api.com/v4/sports/{esporte}/odds"
    params = {
        'apiKey': api_key,
        'regions': 'eu',
        'markets': 'h2h',
        'bookmakers': 'betano,bet365'
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("Erro API:", response.text)
        return []
    return response.json()

def verificar_surebet(odd1, odd2):
    if not odd1 or not odd2:
        return None
    soma_inv = (1 / odd1) + (1 / odd2)
    if soma_inv < 1:
        return round((1 - soma_inv) * 100, 2)
    return None

def analisar_eventos(dados):
    resultados = []
    for evento in dados:
        nome = f"{evento['home_team']} x {evento['away_team']}"
        odds = {}

        for bk in evento['bookmakers']:
            bk_nome = bk['title'].lower()
            if bk_nome in ['betano', 'bet365']:
                try:
                    outcomes = bk['markets'][0]['outcomes']
                    odds[bk_nome] = {o['name']: o['price'] for o in outcomes}
                except:
                    continue

        if 'betano' in odds and 'bet365' in odds:
            for resultado in odds['betano']:
                o1 = odds['betano'].get(resultado)
                o2 = odds['bet365'].get(resultado)
                lucro = verificar_surebet(o1, o2)
                if lucro:
                    resultados.append({
                        'evento': nome,
                        'resultado': resultado,
                        'odd_betano': o1,
                        'odd_bet365': o2,
                        'lucro': lucro
                    })
    return resultados

async def enviar_alerta(mensagem):
    await bot.send_message(chat_id=CHAT_ID, text=mensagem)

async def loop_monitoramento():
    while True:
        for esporte in ESPORTES:
            print(f"Verificando odds para: {esporte}")
            dados = coletar_odds(API_KEY, esporte)
            surebets = analisar_eventos(dados)

            for s in surebets:
                msg = (
                    f"**Surebet Encontrada**\n"
                    f"Evento: {s['evento']}\n"
                    f"Resultado: {s['resultado']}\n"
                    f"Betano: {s['odd_betano']} | Bet365: {s['odd_bet365']}\n"
                    f"Lucro: {s['lucro']:.2f}%"
                )
                await enviar_alerta(msg)

        await asyncio.sleep(180)

if __name__ == "__main__":
    asyncio.run(loop_monitoramento())
