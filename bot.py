import logging
import os
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, ApplicationBuilder, MessageHandler
from ptbcontrib.ptb_jobstores.mongodb import PTBMongoDBJobStore
from aemet import Aemet
from datetime import datetime, timedelta
from tools import get_ranges, get_full_translated_date, get_galician_most_similar_municipality_code

# Set the Telegram bot token
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DB_URI = os.environ.get('MONGODB_URI')

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
  if float(max(filtered_data.values())) == 0:
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
  # STORM
  filtered_data = data["storm_probability"]
  if int(max(filtered_data.values())) > 0:
    text += '⛈ Tormentas:\n'
    if '0208' in filtered_data and int(filtered_data["0208"]) > 0:
      text += f'🕐 Madrugada: {filtered_data["0208"]}%\n'
    if '0814' in filtered_data and int(filtered_data["0814"]) > 0:
      text += f'🕐 Mañá: {filtered_data["0814"]}%\n'
    if '1420' in filtered_data and int(filtered_data["1420"]) > 0:
      text += f'🕐 Tarde: {filtered_data["1420"]}%\n'
    if '2002' in filtered_data and int(filtered_data["2002"]) > 0:
      text += f'🕐 Noite: {filtered_data["2002"]}%\n\n'
  # WIND
  filtered_data = {key: value for key, value in data["wind"].items() if int(key) >= init_hour and int(key) <= end_hour}
  # Get max speed value
  max_speed = max([int(value["speed"]) for value in filtered_data.values()])
  if max_speed > 10:
    text += f'🌬 Vento: Refacho máximo de {max_speed} km/h\n'
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
  text += f'Pola madrugada (de 0 a 6h): {Aemet.get_sky_state_description(data["sky_state"]["00-06"]["sky_code"])}\n'
  text += f'Pola mañá (de 6 a 12h): {Aemet.get_sky_state_description(data["sky_state"]["06-12"]["sky_code"])}\n'
  text += f'Pola tarde (de 12 a 18h): {Aemet.get_sky_state_description(data["sky_state"]["12-18"]["sky_code"])}\n'
  text += f'Pola noite (de 18 a 24h): {Aemet.get_sky_state_description(data["sky_state"]["18-24"]["sky_code"])}\n\n'
  # RAIN PROBABILITY
  filtered_data = {k:v for k, v in dict(data["rain_probability"]).items() if v is not None}
  will_rain = int(max(filtered_data.values())) > 0
  if will_rain:
    text += '💧 Probabilidade de choiva\n'
    text += f'Pola mañá: {data["rain_probability"]["06-12"]}%\n'
    text += f'Pola tarde: {data["rain_probability"]["12-18"]}%\n'
    text += f'Pola noite: {data["rain_probability"]["18-24"]}%\n\n'
  else:
    text += 'Non se esperan precipitacións\n\n'
  # WIND
  # Get max speed value
  # TODO: Get data by time range
  max_speed = max([int(wind_data["speed"]) for wind_data in data["wind"].values()])
  if max_speed > 10:
    text += f'🌬 Vento: Refacho máximo de {max_speed} km/h\n'
  # SNOW
  max_snow_quota = {int(v) for v in data["snow_quota"].values() if v is not None}
  if max_snow_quota and max(max_snow_quota) > 0:
    text += f'🌨 Cota de neve: {max(max_snow_quota)} m\n'
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
  municipality_code, municipality_name = get_galician_most_similar_municipality_code(municipality_name)
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
  municipality_code, municipality_name = get_galician_most_similar_municipality_code(municipality_name)
  if municipality_code is None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Non se atopou o concello.")
    return
  # Get daily forecast from Aemet
  date = datetime.today() + timedelta(days=1)
  data = Aemet.get_daily_forecast(municipality_code, date)
  # Envía la predicción al chat privado del usuario
  await context.bot.send_message(chat_id=update.effective_chat.id, text=get_daily_forecast_text(data, date))

async def send_daily_report(context: ContextTypes.DEFAULT_TYPE):
  municipality_code = context.job.data['municipality_code']
  # Get daily forecast from Aemet
  date = datetime.today() + timedelta(days=1)
  data = Aemet.get_daily_forecast(municipality_code, date)
  # Envía la predicción al chat privado del usuario
  await context.bot.send_message(chat_id=context.job.chat_id, text=get_daily_forecast_text(data, date))
  # Schedule a new job for tomorroy
  run_at = date.replace(hour=21, minute=0, second=0, microsecond=0)
  context.job_queue.run_once(send_daily_report, run_at, data={'municipality_code': municipality_code}, chat_id=context.job.chat_id)

async def schedule_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat_id = update.message.chat_id
  # Get the municipality code
  municipality_name = ' '.join(context.args)
  # Get ,unicipality code
  municipality_code, municipality_name = get_galician_most_similar_municipality_code(municipality_name)
  # If it doesn't exist, send an error message
  if municipality_code is None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Non se atopou o concello.")
    return
  # Schedule the job with the municipality code
  today = datetime.now()
  run_at = today.replace(hour=21, minute=0, second=0, microsecond=0)
  context.job_queue.run_once(send_daily_report, run_at, data={'municipality_code': municipality_code}, chat_id=chat_id)
  await context.bot.send_message(chat_id=chat_id, text=f'Envío de reporte diario configurado para {municipality_name}')

def main():
    # Create the bot
    application = ApplicationBuilder().token(TOKEN).build()
    # Commands
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('tempo', prediccion))
    application.add_handler(CommandHandler('mana', tomorrow_prediccion))
    application.add_handler(CommandHandler('reporte', schedule_report))
    # Jobs manager
    application.job_queue.scheduler.add_jobstore(
        PTBMongoDBJobStore(
            application=application,
            host=DB_URI,
        )
    )
    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
