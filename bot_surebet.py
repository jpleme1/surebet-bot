import os
import requests
from telegram import Bot
from telegram.ext import Updater, CommandHandler

# Acessar as variáveis de ambiente para o token do bot e a chave da API de odds
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Token do bot do Telegram
ODDS_API_KEY = os.getenv('ODDS_API_KEY')  # Chave da API de odds

# Verifique se as variáveis de ambiente estão configuradas corretamente
if TELEGRAM_BOT_TOKEN is None or ODDS_API_KEY is None:
    print("Erro: As variáveis de ambiente TELEGRAM_BOT_TOKEN ou ODDS_API_KEY não estão configuradas.")
    exit(1)

# Função para enviar mensagem ao Telegram
def start(update, context):
    update.message.reply_text("Olá! Eu sou o bot de Surebet! Eu vou te ajudar a encontrar as melhores odds!")

# Função para verificar as odds e calcular a surebet
def check_surebet(update, context):
    # Aqui você pode fazer uma chamada para a API de odds e comparar as odds entre as casas
    try:
        # Exemplo de como pegar as odds da API (isso depende de como a API funciona)
        url = f"https://api.exemplo.com/odds?api_key={ODDS_API_KEY}"  # Substitua pela URL correta da API
        response = requests.get(url)
        data = response.json()

        # Logica para verificar as odds e encontrar a surebet
        # Exemplo simplificado (depende da estrutura da resposta da API)
        odds_betano = data['betano']['odds']
        odds_bet365 = data['bet365']['odds']
        
        # Exemplo de cálculo simplificado para localizar uma surebet (apenas um exemplo)
        if odds_betano > odds_bet365:
            message = f"A melhor odd está na Betano: {odds_betano}"
        else:
            message = f"A melhor odd está na Bet365: {odds_bet365}"

        update.message.reply_text(message)
    
    except Exception as e:
        update.message.reply_text(f"Ocorreu um erro: {str(e)}")

# Função para iniciar o bot
def main():
    # Criar o updater e o dispatcher
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Adicionar handlers para comandos do Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("check_surebet", check_surebet))

    # Iniciar o bot
    updater.start_polling()
    updater.idle()

if _name_ == '_main_':
    main()