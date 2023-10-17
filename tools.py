import jellyfish
import csv

def get_ranges(lst):
  ranges = []
  start = end = lst[0]
  for i in range(1, len(lst)):
    if lst[i] == end + 1:
      end = lst[i]
    else:
      ranges.append((start, end))
      start = end = lst[i]
  ranges.append((start, end))
  return ranges

def get_translated_month(date):
  month = date.strftime('%b')
  if month == 'Jan':
    return 'Xan'
  elif month == 'Feb':
    return 'Feb'
  elif month == 'Mar':
    return 'Mar'
  elif month == 'Apr':
    return 'Abr'
  elif month == 'May':
    return 'Mai'
  elif month == 'Jun':
    return 'Xun'
  elif month == 'Jul':
    return 'Xul'
  elif month == 'Aug':
    return 'Ago'
  elif month == 'Sep':
    return 'Set'
  elif month == 'Oct':
    return 'Out'
  elif month == 'Nov':
    return 'Nov'
  elif month == 'Dec':
    return 'Dec'
  else:
    return month

def get_translated_weekday(date):
  weekday = date.weekday()
  if weekday == 1:
    return 'Luns'
  elif weekday == 2:
    return 'Martes'
  elif weekday == 3:
    return 'Mércores'
  elif weekday == 4:
    return 'Xoves'
  elif weekday == 5:
    return 'Venres'
  elif weekday == 6:
    return 'Sábado'
  elif weekday == 7:
    return 'Domingo'
  else:
    return weekday

def get_full_translated_date(date):
  return f'{get_translated_weekday(date)}, {date.day} de {get_translated_month(date)} de {date.year}'

def get_galician_most_similar_municipality_code(municipality_name):
  # Get municipalities from CSV file. CSV was downloaded from INE website:
  # https://www.ine.es/daco/daco42/codmun/codmunmapa.htm
  filename = 'data/meteogalicia_municipalities.csv'
  municipalities = []
  with open(filename, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    for row in reader:
      # If municipality name is similar to the one provided, add it to the list
      if jellyfish.jaro_winkler_similarity(municipality_name, row[1]) > 0.8:
        municipalities.append(row)
  # Get the most similar municipality
  municipality_data = sorted(municipalities, key=lambda x: jellyfish.jaro_winkler_similarity(municipality_name, x[1]), reverse=True)
  if len(municipality_data) > 0:
    municipality_data = municipality_data[0]
    return (municipality_data[0], municipality_data[1])
  else:
    return (None, None)

def get_spain_most_similar_municipality_code(municipality_name):
  # Get municipalities from CSV file. CSV was downloaded from INE website:
  # https://www.ine.es/daco/daco42/codmun/codmunmapa.htm
  filename = 'data/municipalities_codes.csv'
  municipalities = []
  with open(filename, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    for row in reader:
      # If municipality name is similar to the one provided, add it to the list
      if jellyfish.jaro_winkler_similarity(municipality_name, row[4]) > 0.9:
        municipalities.append(row)
  # Get the most similar municipality
  municipality_data = sorted(municipalities, key=lambda x: jellyfish.jaro_winkler_similarity(municipality_name, x[4]), reverse=True)
  if len(municipality_data) > 0:
    municipality_data = municipality_data[0]
    return (f'{municipality_data[1]}{municipality_data[2]}', municipality_data[4])
  else:
    return (None, None)
