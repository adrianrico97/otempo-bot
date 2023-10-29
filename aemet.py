import requests
import xml.etree.ElementTree as ET
import re
from datetime import date, datetime

class Aemet:
  BASE_URL = 'https://www.aemet.es'

  # Description in Spanish (es) and Galician (gal) for each Aemet icon code.
  # If the code contains a 'n' at the end, it means that it is night. Night description are not included in this JSON.
  # The night description is the same as the day description, but with a 'noche' at the end. Example: 'Despejado' -> 'Despejado noche'
  # Source: https://www.aemet.es/es/eltiempo/prediccion/espana/ayuda
  SKY_STATE_CODES_DESCRIPTION = {
    11: {'es': 'Despejado', 'gal': 'Despexado'},
    12: {'es': 'Poco nuboso', 'gal': 'Pouco nubrado'},
    13: {'es': 'Intervalos nubosos', 'gal': 'Intervalos nubrados'},
    14: {'es': 'Nuboso', 'gal': 'Nubrado'},
    15: {'es': 'Muy nuboso', 'gal': 'Moi nubrado'},
    16: {'es': 'Cubierto', 'gal': 'Cuberto'},
    17: {'es': 'Nubes altas', 'gal': 'Nubes altas'},
    23: {'es': 'Intervalos nubosos con lluvia', 'gal': 'Intervalos nubrados con choiva'},
    24: {'es': 'Nuboso con lluvia', 'gal': 'Nubrado con choiva'},
    25: {'es': 'Muy nuboso con lluvia', 'gal': 'Moi nubrado con choiva'},
    26: {'es': 'Cubierto con lluvia', 'gal': 'Cuberto con choiva'},
    33: {'es': 'Intervalos nubosos con nieve', 'gal': 'Intervalos nubrados con neve'},
    34: {'es': 'Nuboso con nieve', 'gal': 'Nubrado con neve'},
    35: {'es': 'Muy nuboso con nieve', 'gal': 'Moi nubrado con neve'},
    36: {'es': 'Cubierto con nieve', 'gal': 'Cuberto con neve'},
    43: {'es': 'Intervalos nubosos con lluvia escasa', 'gal': 'Intervalos nubrados con choiva escasa'},
    44: {'es': 'Nuboso con lluvia escasa', 'gal': 'Nubrado con choiva escasa'},
    45: {'es': 'Muy nuboso con lluvia escasa', 'gal': 'Moi nubrado con choiva escasa'},
    46: {'es': 'Cubierto con lluvia escasa', 'gal': 'Cuberto con choiva escasa'},
    51: {'es': 'Intervalos nubosos con tormenta', 'gal': 'Intervalos nubrados con tormenta'},
    52: {'es': 'Nuboso con tormenta', 'gal': 'Nubrado con tormenta'},
    53: {'es': 'Muy nuboso con tormenta', 'gal': 'Moi nubrado con tormenta'},
    54: {'es': 'Cubierto con tormenta', 'gal': 'Cuberto con tormenta'},
    61: {'es': 'Intervalos nubosos con tormenta y lluvia escasa', 'gal': 'Intervalos nubrados con tormenta e choiva escasa'},
    62: {'es': 'Nuboso con tormenta y lluvia escasa', 'gal': 'Nubrado con tormenta e choiva escasa'},
    63: {'es': 'Muy nuboso con tormenta y lluvia escasa', 'gal': 'Moi nubrado con tormenta e choiva escasa'},
    64: {'es': 'Cubierto con tormenta y lluvia escasa', 'gal': 'Cuberto con tormenta e choiva escasa'},
    71: {'es': 'Intervalos nubosos con nieve escasa', 'gal': 'Intervalos nubrados con neve escasa'},
    72: {'es': 'Nuboso con nieve escasa', 'gal': 'Nubrado con neve escasa'},
    73: {'es': 'Muy nuboso con nieve escasa', 'gal': 'Moi nubrado con neve escasa'},
    74: {'es': 'Cubierto con nieve escasa', 'gal': 'Cuberto con neve escasa'},
    81: {'es': 'Niebla', 'gal': 'Néboa'},
    82: {'es': 'Bruma', 'gal': 'Brétema'},
    83: {'es': 'Calima', 'gal': ''},
  }

  def get_daily_forecast(municipality, forecast_date = date.today()):
    url = f'{Aemet.BASE_URL}/xml/municipios/localidad_{municipality}.xml'
    # Make the request
    response = requests.get(url)
    data = ET.fromstring(response.text)
    return Aemet.__parse_daily_forecast(data, forecast_date)

  def get_hourly_forecast(municipality, forecast_date = date.today()):
    url = f'{Aemet.BASE_URL}/xml/municipios_h/localidad_h_{municipality}.xml'
    # Make the request
    response = requests.get(url)
    data = ET.fromstring(response.text)
    return Aemet.__parse_hourly_forecast(data, forecast_date)

  def get_sky_state_description(code, language='gal'):
    if code is None:
      return ''
    code = int(re.sub('n', '', code))
    return Aemet.SKY_STATE_CODES_DESCRIPTION[code][language]

  def __parse_daily_forecast(data, forecast_date):
    forecast_data = {}
    # Get location data
    forecast_data['location'] = data.find('nombre').text
    forecast_data['province'] = data.find('provincia').text
    forecast_data['updated_at'] = data.find('elaborado').text
    # Get the forecast for today
    if isinstance(forecast_date, datetime):
      forecast_date = forecast_date.date()
    today_data = data.find('prediccion').find(f'.//dia[@fecha="{forecast_date.isoformat()}"]')
    # Get sky state
    forecast_data['sky_state'] = {}
    for estado_cielo in today_data.findall('estado_cielo'):
      forecast_data['sky_state'][estado_cielo.attrib['periodo']] = {
        'description': estado_cielo.attrib['descripcion'],
        'sky_code': estado_cielo.text,
      }
    # Get max and min temperature
    forecast_data['temperature'] = {}
    temperature_data = today_data.find('temperatura')
    forecast_data['temperature']['max'] = temperature_data.find('maxima').text
    forecast_data['temperature']['min'] = temperature_data.find('minima').text
    forecast_data['temperature']['hourly'] = {}
    for temperature in temperature_data.findall('dato'):
      forecast_data['temperature']['hourly'][temperature.attrib['hora']] = temperature.text
    # Get sensation temperature
    forecast_data['temperature_sensation'] = {}
    temp_sens_data = today_data.find('sens_termica')
    forecast_data['temperature_sensation']['max'] = temp_sens_data.find('maxima').text
    forecast_data['temperature_sensation']['min'] = temp_sens_data.find('minima').text
    forecast_data['temperature_sensation']['hourly'] = {}
    for temperature_sensation in temp_sens_data.findall('dato'):
      forecast_data['temperature_sensation']['hourly'][temperature_sensation.attrib['hora']] = temperature_sensation.text
    # Get precipitation probability
    forecast_data['rain_probability'] = {}
    for rain_probability in today_data.findall('prob_precipitacion'):
      forecast_data['rain_probability'][rain_probability.attrib['periodo']] = rain_probability.text
    # Get wind
    forecast_data['wind'] = {}
    for wind in today_data.findall('viento'):
      forecast_data['wind'][wind.attrib['periodo']] = {
        'direction': wind.find('direccion').text,
        'speed': wind.find('velocidad').text,
      }
    # Get snow qouta
    forecast_data['snow_quota'] = {}
    for cota_nieve_prov in today_data.findall('cota_nieve_prov'):
      forecast_data['snow_quota'][cota_nieve_prov.attrib['periodo']] = cota_nieve_prov.text
    # Return JSON
    return forecast_data

  def __parse_hourly_forecast(data, forecast_date):
    forecast_data = {}
    # Get location data
    forecast_data['location'] = data.find('nombre').text
    forecast_data['province'] = data.find('provincia').text
    forecast_data['updated_at'] = data.find('elaborado').text
    # Get the forecast for today
    if isinstance(forecast_date, datetime):
      forecast_date = forecast_date.date()
    today_data = data.find('prediccion').find(f'.//dia[@fecha="{forecast_date.isoformat()}"]')
    # Get sunrise and sunset
    forecast_data['sunrise'] = today_data.attrib['orto']
    forecast_data['sunset'] = today_data.attrib['ocaso']
    # Get sky state
    forecast_data['sky_state'] = {}
    for estado_cielo in today_data.findall('estado_cielo'):
      forecast_data['sky_state'][estado_cielo.attrib['periodo']] = {
        'description': estado_cielo.attrib['descripcion'],
        'sky_code': estado_cielo.text,
      }
    # Get rain values
    forecast_data['rain'] = {}
    for rain in today_data.findall('precipitacion'):
      forecast_data['rain'][rain.attrib['periodo']] = rain.text
    # Get rain probability
    forecast_data['rain_probability'] = {}
    for rain_probability in today_data.findall('prob_precipitacion'):
      forecast_data['rain_probability'][rain_probability.attrib['periodo']] = rain_probability.text
    # Get temperature
    forecast_data['temperature'] = {}
    for temperature in today_data.findall('temperatura'):
      forecast_data['temperature'][temperature.attrib['periodo']] = temperature.text
    # Get temperature sensation
    forecast_data['temperature_sensation'] = {}
    for temperature_sensation in today_data.findall('sens_termica'):
      forecast_data['temperature_sensation'][temperature_sensation.attrib['periodo']] = temperature_sensation.text
    # Get storm probability
    forecast_data['storm_probability'] = {}
    for storm_probability in today_data.findall('prob_tormenta'):
      forecast_data['storm_probability'][storm_probability.attrib['periodo']] = storm_probability.text
    # Get wind
    forecast_data['wind'] = {}
    for wind in today_data.findall('viento'):
      forecast_data['wind'][wind.attrib['periodo']] = {
        'direction': wind.find('direccion').text,
        'speed': wind.find('velocidad').text,
      }
    # Return JSON
    return forecast_data
