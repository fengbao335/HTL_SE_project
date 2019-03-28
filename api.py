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
APIKEY = '5979ce80578015211c5630d5d3762548e5eba68d'
NAME = "Dublin"
STATIONS_URI = "https://api.jcdecaux.com/vls/v1/stations"
engine = create_engine("mysql+mysqldb://{}:{}@{}:{}/{}".format("HTL", "HTL123456", "dbbikes.cfhvz7o7yt2w.us-east-1.rds.amazonaws.com", "3306", "dbbikes"), echo=True)
while True:
    r = requests.get(STATIONS_URI, params={"apiKey": APIKEY, "contract": NAME})
    stations = (json.loads(r.text))
    for station in stations:
        vals = (station.get('address'), station.get('available_bike_stands'), station.get('available_bikes'), station.get('banking'), station.get('bike_stands'), station.get('bonus'),  station.get('contract_name'), station.get('last_update'), station.get('name'), station.get('number'), station.get('position').get('lat'), station.get('position').get('lng'), station.get('status'))
        engine.execute("insert into STATION(address, available_bike_stands, available_bikes, banking, bike_stands, bonus, contract_name, last_update, name, number, position_lat, position_lng, status)values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", vals)
    time.sleep(5*60)