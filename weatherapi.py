import MySQLdb
import requests
import json
import sqlalchemy as sqla
from sqlalchemy import create_engine
import traceback
import glob
import os
import requests
import time
import datetime
from IPython.display import display
APIKEY = '9511c6f09bf671d3bd65bf650197234f'
NAME = "Dublin"
WEATHER_URI = "http://api.openweathermap.org/data/2.5/weather?q=Dublin"
engine = create_engine("mysql+mysqldb://{}:{}@{}:{}/{}".format("HTL", "HTL123456", "dbbikes.cfhvz7o7yt2w.us-east-1.rds.amazonaws.com", "3306", "dbbikes"), echo=True)
while True:
    r = requests.get(WEATHER_URI, params={"apiKey": APIKEY, "contract": NAME})
    weather = (json.loads(r.text))
	vals = (weather.get('dt'), weather.get('main').get('humidity'), weather.get('main').get('pressure'), weather.get('main').get('temp'), weather.get('main').get('temp_max'), weather.get('main').get('temp_min'),  weather.get('weather')[0].get('description'), weather.get('weather')[0].get('icon'), weather.get('weather')[0].get('id'), weather.get('weather')[0].get('main'), weather.get('wind').get('deg'), weather.get('wind').get('speed'))
	engine.execute("insert into WEATHER(dt, humidity, pressure, temp, temp_max, temp_min, description, icon, id, main, wind_deg, wind_speed)values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", vals)
    time.sleep(60*60)