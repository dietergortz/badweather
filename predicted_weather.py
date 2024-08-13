from bs4 import BeautifulSoup as bs
from datetime import datetime as dt, timedelta
import pandas as pd
import requests
import re
import db_connect # Hides my passwords
import pytz
import sys

utc_now = dt.now(pytz.utc)
london_tz = pytz.timezone('Europe/London')
current_date = utc_now.astimezone(london_tz)
current_hour = current_date.time().hour
days_to_capture = 4

# Since PythonAnywhere's tasks cannot be configured to specific time zones
# I need to run the task every hour and check if the converted hour is correct.
if current_hour != 12:
   sys.exit()

url = 'https://www.bbc.co.uk/weather/2643743'
head = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
}

forecast_class = 'wr-time-slot__inner'
hours_class = 'wr-time-slot-primary__hours'
description_class = 'wr-time-slot-primary__weather-type-description'
temperature_class = 'wr-value--temperature--c'
precipitation_class = 'wr-time-slot-primary__precipitation'
rain_text_class = 'wr-u-font-weight-500'

predicted_weather = []

for i in range(days_to_capture):
    date = current_date.date() + timedelta(days=i)
    response = requests.get(url + '/day' + str(i), headers=head)
    
    if i == 0:
        hours = ['12', '13', '15', '18', '00']
    else:
        hours = ['12']

    if response.status_code == 200:
        soup = bs(response.text, 'html.parser')
        forecast = soup.select(f'button[class^="{forecast_class}"]')

        if forecast:
            for item in forecast:
                hour = item.find('span', class_=f'{hours_class}')
                type = None
                temp = None
                chance = None

                if hour.text in hours:
                    type = item.find('div', class_=f'{description_class}')
                    
                    temp = item.find('span', class_=f'{temperature_class}')
                    if temp:
                        temp = re.search(r'\d+', temp.text)
                        if temp:
                            temp = temp.group()

                    rain = item.find('div', class_=f'{precipitation_class}')
                    if rain:
                        chance = rain.find('div', class_=f'{rain_text_class}')
                        if chance:
                            chance = re.search(r'\d+', chance.text)
                            if chance:
                                chance = chance.group()

                    predicted_weather.append([date, 1, i, int(hour.text), type.text.lower(), int(temp), int(chance)])

if len(predicted_weather) > 0:
    tunnel = db_connect.open_tunnel()
    tunnel.start()
    engine = db_connect.start_engine(tunnel)

    headers = ['date', 'prediction', 'day_offset', 'time', 'type', 'temp', 'rain']
    predicted_weather = pd.DataFrame(predicted_weather, columns=headers)
    predicted_weather.to_sql(name='weather_data', con=engine, if_exists='replace', index=False)

    tunnel.stop()