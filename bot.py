import logging
import os
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, ApplicationBuilder
from aemet import Aemet
from datetime import datetime, timedelta
from tools import get_ranges, get_full_translated_date

# Set the Telegram bot token
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  level=logging.INFO
)

def get_hourly_forecast_text(data, date):
  # Build the text
  text = f'Predición para {data["location"]} ({data["province"]}).\n{get_full_translated_date(date)}\n\n'
  text += f'🌅 Saída do sol: {data["sunrise"]}\n'
  text += f'🌇 Posta do sol: {data["sunset"]}\n\n'
  # Time range
  current_hour = int(datetime.now().strftime('%H'))
  init_hour = current_hour
  end_hour = current_hour + 6
  # 23 is the last hour of the day
  if end_hour > 23:
    end_hour = 23
  text += f'🕐 Predición para as {init_hour}h ata as {end_hour}h\n\n'
  # TEMPERATURE
  text += '🌡 Temperatura\n'
  filtered_data = {key: value for key, value in data["temperature"].items() if int(key) >= init_hour and int(key) <= end_hour}
  text += f'Máxima: {max(filtered_data.values())}ºC\n'
  text += f'Mínima: {min(filtered_data.values())}ºC\n\n'
  # SKY STATE
  text += '☁️ Estado do ceo\n'
  filtered_data = {key: value for key, value in data["sky_state"].items() if int(key) >= init_hour and int(key) <= end_hour}
  for key, value in filtered_data.items():
    text += f'Ás {key}h: {Aemet.get_sky_state_description(value["sky_code"])}\n'
  # RAIN
  will_rain = False
  text += '\n🌧 Precipitación\n'
  filtered_data = {key: value for key, value in data["rain"].items() if float(key) >= init_hour and float(key) <= end_hour}
  if int(max(filtered_data.values())) == 0:
    text += 'Non se esperan precipitacións\n'
  else:
    will_rain = True
    filtered_data = {key: value for key, value in data["rain"].items() if float(value) > 0}
    rain_ranges = get_ranges([int(key) for key in filtered_data.keys()])
    text += f'Espérase choiva:\n'
    for rain_range in rain_ranges:
      if rain_range[0] == rain_range[1]:
        text += f'\tÁs {rain_range[0]}h\n'
      else:
        text += f'\tEntre as {rain_range[0]}h e as {rain_range[1]}h\n'
  # RAIN PROBABILITY
  if will_rain:
    text += '\n💧 Probabilidade de choiva\n'
    if '0208' in data["rain_probability"]:
      text += f'🕐 Madrugada: {data["rain_probability"]["0208"]}%\n'
    if '0814' in data["rain_probability"]:
      text += f'🕐 Mañá: {data["rain_probability"]["0814"]}%\n'
    if '1420' in data["rain_probability"]:
      text += f'🕐 Tarde: {data["rain_probability"]["1420"]}%\n'
    if '2002' in data["rain_probability"]:
      text += f'🕐 Noite: {data["rain_probability"]["2002"]}%\n\n'
  return text

def get_daily_forecast_text(data, date):
  # Build the text
  text = f'Predición para {data["location"]} ({data["province"]}).\n'
  text += f'{get_full_translated_date(date)}\n\n'
  # TEMPERATURE
  text += '🌡 Temperatura\n'
  text += f'Máxima: {data["temperature"]["max"]}ºC (sensación térmica: {data["temperature_sensation"]["max"]}ºC)\n'
  text += f'Mínima: {data["temperature"]["min"]}ºC (sensación térmica: {data["temperature_sensation"]["min"]}ºC)\n\n'
  # SKY STATE
  text += '☁️ Estado do ceo\n'
  text += f'Pola mañá: {Aemet.get_sky_state_description(data["sky_state"]["06-12"]["sky_code"])}\n'
  text += f'Pola tarde: {Aemet.get_sky_state_description(data["sky_state"]["12-18"]["sky_code"])}\n'
  text += f'Pola noite: {Aemet.get_sky_state_description(data["sky_state"]["18-24"]["sky_code"])}\n\n'
  # RAIN PROBABILITY
  will_rain = int(max(data["rain_probability"].values())) > 0
  if will_rain:
    text += '💧 Probabilidade de choiva\n'
    text += f'Pola mañá: {data["rain_probability"]["06-12"]}%\n'
    text += f'Pola tarde: {data["rain_probability"]["12-18"]}%\n'
    text += f'Pola noite: {data["rain_probability"]["18-24"]}%\n\n'
  else:
    text += 'Non se esperan precipitacións\n\n'
  return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(chat_id=update.effective_chat.id, text="¡Ola! Envía /tempo seguido do concello para obter a predición.")

async def prediccion(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if context.args is None or len(context.args) == 0:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Envía /tempo seguido do nome dun concello para obter a predición.")
    return
  # Get municipality name and forecast
  municipality_name = ' '.join(context.args)
  # Get ,unicipality code
  municipality_code, municipality_name = Aemet.most_similar_municipality_code(municipality_name)
  if municipality_code is None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Non se atopou o concello.")
    return
  # Get daily forecast from Aemet
  date = datetime.today()
  data = Aemet.get_hourly_forecast(municipality_code, date)
  # Envía la predicción al chat privado del usuario
  await context.bot.send_message(chat_id=update.effective_chat.id, text=get_hourly_forecast_text(data, date))

async def tomorrow_prediccion(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if context.args is None or len(context.args) == 0:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Envía /dia seguido do nome dun concello para obter a predición.")
    return
  # Get municipality name and forecast
  municipality_name = ' '.join(context.args)
  # Get ,unicipality code
  municipality_code, municipality_name = Aemet.most_similar_municipality_code(municipality_name)
  if municipality_code is None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Non se atopou o concello.")
    return
  # Get daily forecast from Aemet
  date = datetime.today() + timedelta(days=1)
  data = Aemet.get_daily_forecast(municipality_code, date)
  # Envía la predicción al chat privado del usuario
  await context.bot.send_message(chat_id=update.effective_chat.id, text=get_daily_forecast_text(data, date))

def main():
    # Create the bot
    application = ApplicationBuilder().token(TOKEN).build()
    # Commands
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('tempo', prediccion))
    application.add_handler(CommandHandler('mana', tomorrow_prediccion))
    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
