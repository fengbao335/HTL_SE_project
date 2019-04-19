#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# import all required package
import pymysql
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


# In[ ]:


#set up connection with database
engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format("HTL", "HTL123456", "dbbikes.c48xjvxqywhq.us-east-1.rds.amazonaws.com", "3306", "dbbikes"), echo=True)


# In[ ]:


#Create table STATION
create_table_stand = """
CREATE TABLE IF NOT EXISTS STATION(
address VARCHAR(256),
available_bike_stands INTEGER,
available_bikes INTEGER,
banking VARCHAR(256),
bike_stands INTEGER,
bonus VARCHAR(256),
contract_name VARCHAR(256),
last_update VARCHAR(256),
name VARCHAR(256),
number INTEGER,
position_lat REAL,
position_lng REAL,
status VARCHAR(256)
)"""
try:
    res = engine.execute(create_table_stand)
    print(res.fetchall())
except Exception as e:
    print(e)


# In[ ]:


#Create table WEATHER
create_table_stand = """
CREATE TABLE IF NOT EXISTS WEATHER(
dt INTEGER,
humidity INTEGER,
pressure INTEGER,
temp DOUBLE,
temp_max DOUBLE,
temp_min DOUBLE,
decription VARCHAR(256),
icon VARCHAR(256),
id INTEGER,
main VARCHAR(256),
wind_leg INTEGER,
wind_speed DOUBLE,
)"""
try:
    res = engine.execute(create_table_stand)
    print(res.fetchall())
except Exception as e:
    print(e)


# In[ ]:


APIKEY = '5979ce80578015211c5630d5d3762548e5eba68d'
NAME = "Dublin"
STATIONS_URI = "https://api.jcdecaux.com/vls/v1/stations"
#set up connection with RDS
engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format("HTL", "HTL123456", "dbbikes.c48xjvxqywhq.us-east-1.rds.amazonaws.com", "3306", "dbbikes"), echo=True)
#send requests to get station API information
r = requests.get(STATIONS_URI, params={"apiKey": APIKEY, "contract": NAME})
stations = (json.loads(r.text))
for station in stations:
    #insert JSON data to database every 5 mins
    vals = (station.get('address'), station.get('available_bike_stands'), station.get('available_bikes'), station.get('banking'), station.get('bike_stands'), station.get('bonus'),  station.get('contract_name'), station.get('last_update'), station.get('name'), station.get('number'), station.get('position').get('lat'), station.get('position').get('lng'), station.get('status'))
    engine.execute("insert into STATIONS(address, available_bike_stands, available_bikes, banking, bike_stands, bonus, contract_name, last_update, name, number, position_lat, position_lng, status)values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", vals)


# In[ ]:


APIKEY = '9511c6f09bf671d3bd65bf650197234f'
NAME = "Dublin"
WEATHER_URI = "http://api.openweathermap.org/data/2.5/weather?q=Dublin"
#set up connection with RDS
engine = create_engine("mysql+mysqldb://{}:{}@{}:{}/{}".format("HTL", "HTL123456", "dbbikes.c48xjvxqywhq.us-east-1.rds.amazonaws.com", "3306", "dbbikes"), echo=True)
while True:
    #send requests to get station API information
    r = requests.get(WEATHER_URI, params={"apiKey": APIKEY, "contract": NAME})
    weather = (json.loads(r.text))
    #insert JSON data to database every one hour
    vals = (weather.get('dt'), weather.get('main').get('humidity'), weather.get('main').get('pressure'), weather.get('main').get('temp'), weather.get('main').get('temp_max'), weather.get('main').get('temp_min'),  weather.get('weather')[0].get('description'), weather.get('weather')[0].get('icon'), weather.get('weather')[0].get('id'), weather.get('weather')[0].get('main'), weather.get('wind').get('deg'), weather.get('wind').get('speed'))
    engine.execute("insert into WEATHER(dt, humidity, pressure, temp, temp_max, temp_min, description, icon, id, main, wind_deg, wind_speed)values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", vals)
    time.sleep(60*60)

