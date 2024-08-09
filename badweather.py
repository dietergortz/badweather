from bs4 import BeautifulSoup as bs
from datetime import datetime as dt, timedelta
import requests
import re

current_date = dt.now().date()
current_time = dt.now().time().hour
days_to_capture = 2
year = current_date.year

url = 'https://www.bbc.co.uk/weather/2643743'
head = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
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

weather_data = []

for i in range(days_to_capture):
    date = current_date + timedelta(days=i)
    response = requests.get(url + '/day' + str(i), headers=head)
    
    if i == 0:
        hours = ['12', '13', '15', '18', '00']
    else:
        hours = ['12']

    if response.status_code == 200:
        soup = bs(response.text, 'html.parser')
        forecast = soup.select(f'button[class^="{forecast_class}"]')

        if forecast:
            #weather_data.append(return_forecast(forecast, date, hours))
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

                    weather_data.append([date, 1, i, int(hour.text), type.text.lower(), int(temp), int(chance)])

print(weather_data)