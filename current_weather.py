from bs4 import BeautifulSoup as bs
from datetime import datetime as dt, timedelta
import requests
import re

current_date = dt.now().date()
current_time = dt.now().time().hour
year = current_date.year
weather_data = []

url = 'https://www.yr.no/en/forecast/daily-table/2-2643743/United%20Kingdom/England/Greater%20London/London'
head = {
    'Accept': 'image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
}

response = requests.get(url, headers=head)

if response.status_code == 200:
    soup = bs(response.text, 'html.parser')
    current_weather = soup.select('div[class^="now-hero__next-hour-content"]')

    if current_weather:
        for item in current_weather:
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

            weather_data.append([current_date, False, 0, current_time, type, int(temp), int(rain)])

            break

print(weather_data)