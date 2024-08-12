from bs4 import BeautifulSoup as bs
from datetime import datetime as dt
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
year = current_date.year

# Since PythonAnywhere's tasks cannot be configured to specific time zones
# I need to run the task every hour and check if the converted hour is correct.
if current_hour not in (12, 13, 15, 18, 00):
    sys.exit()

url = 'https://www.yr.no/en/forecast/daily-table/2-2643743/United%20Kingdom/England/Greater%20London/London'
head = {
    'Accept': 'image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
}

response = requests.get(url, headers=head)
current_weather = []

if response.status_code == 200:
    soup = bs(response.text, 'html.parser')
    weather_data = soup.select('div[class^="now-hero__next-hour-content"]')

    if weather_data:
        for item in weather_data:
            type = item.find('img', class_='weather-symbol__img')
            if type:
                type = type.get('alt')

            temp = item.find('span', class_=re.compile(r'^temperature'))
            if temp:
                temp = re.search(r'\d+', temp.text)
                if temp:
                    temp = temp.group()

            rain = item.find('span', 'now-hero__next-hour-precipitation-value')
            if rain:
                rain = rain.text

            current_weather.append([current_date, 0, 0, current_hour, type, int(temp), int(rain)])

            break

if len(current_weather) > 0:
    tunnel = db_connect.open_tunnel()
    tunnel.start()
    engine = db_connect.start_engine(tunnel)

    headers = ['date', 'prediction', 'day_offset', 'time', 'type', 'temp', 'rain']
    current_weather = pd.DataFrame(current_weather, columns=headers)
    current_weather.to_sql(name='weather_data', con=engine, if_exists='replace', index=False)

    tunnel.stop()