#!/usr/bin/env python
from flask import Flask, render_template, g, jsonify, request
import requests
import json
from sqlalchemy import create_engine
import time
import pandas as pd
import numpy as np
import pickle


app = Flask(__name__, static_url_path='')
app.config.from_object('config')


@app.route('/')
@app.route('/index')
def root():
    return render_template('index.html')


@app.route('/gallery')
def page2():
    return render_template('gallery.html')


def connect_to_database():
    with open('config.config', 'r') as f: #Open and read the configuration file
        config = json.load(f)       #creat a variable to store the loaded contians
    engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(config['USER'],
                                                                   config['PASSWORD'],
                                                                   config['URI'],
                                                                   config['PORT'],
                                                                   config['DB']), echo=True)
    return engine


def get_db():

    """Save the data fetched from the database to the variable：db"""

    db = getattr(g, '_database', None)
    if db is None:
        db = connect_to_database()
        g.__database = db
    print("Database connected")
    return db


@app.teardown_appcontext
def close_connection(exception):

    """close the connection with database"""

    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/dynamic_stations")
def dynamic_stations():

    """
    fetch data through JCDecaux API,Store data in json format and send to web page host:5000/dynamic_stations
    """

    APIKEY = '5979ce80578015211c5630d5d3762548e5eba68d'
    NAME = "Dublin"
    STATIONS_URI = "https://api.jcdecaux.com/vls/v1/stations"
    temp = requests.get(STATIONS_URI, params={"apiKey": APIKEY, "contract": NAME})
    stations_detail = json.loads(temp.text)
    return jsonify(stations=stations_detail)


@app.route("/daily/<int:station_id>")
def week_chart(station_id):

    """
    This function is used to send the average daily occupancy of the site corresponding to the parameter to the corresponding URL.
    """

    engine = get_db()
    # According to the parameter:station_id
    # select the occupancy of the corresponding station from the database.
    sql = "SELECT available_bikes, available_bike_stands, last_update FROM STATION where number={};".format(station_id)
    rows = engine.execute(sql).fetchall()

    week_average_bikes = []
    week_average_stands = []

    # The values 0 - 6 in the list day represent the days from Sunday to Saturday
    days = [0, 1, 2, 3, 4, 5, 6]
    for day in days:
        # Invoking the function:day_avg, calculate the average occupancy on a single day, and then add it to the list
        week_average_bikes.append(day_avg(rows, day)[0])
        week_average_stands.append(day_avg(rows, day)[1])
    daily = jsonify(week_average_bikes=week_average_bikes, week_average_stands=week_average_stands)
    return daily


def day_avg(rows, day):

    """This function calculates the average of occupancy on a single day"""

    available_bikes = []
    available_bike_stands = []

    for row in rows:
        # Convert Unix stamp to Numbers 0-6, representing Sunday to Saturday
        unix_stamp = time.localtime(int(row["last_update"]))
        weekday = int(time.strftime("%w", unix_stamp))
        if weekday == day:
            available_bikes.append(row["available_bikes"])
            available_bike_stands.append(row["available_bike_stands"])

    day_avg_bikes = int(round((sum(available_bikes) / len(available_bikes)), 0))
    day_avg_bike_stands = int(round((sum(available_bike_stands) / len(available_bike_stands)), 0))

    return day_avg_bikes, day_avg_bike_stands


@app.route("/bikes_prediction/<int:station_id>/<int:time_hour>")
def bikes_prediction(station_id,time_hour):

    """
    This function predicts the occupancy of selected station, depending on the model we trained
    """

    # get the data through openWeather api
    r = requests.get('http://api.openweathermap.org/data/2.5/forecast?appid=9511c6f09bf671d3bd65bf650197234f&q=Dublin')
    weathers = r.json()

    weather_detalis = weathers["list"]
    temp = weather_detalis[0]['main']['temp']
    wind = weather_detalis[0]['wind']['speed']
    main = weather_detalis[0]['weather'][0]['main']
    weather_Drizzle = 0
    weather_Rain = 0
    if main == 'Drizzle':
        weather_Drizzle = 1
    elif main == 'Rain':
        weather_Rain = 1
    f2 = pd.DataFrame(np.array([station_id, time_hour, temp, wind, weather_Drizzle, weather_Rain])).T
    models = {}
    # open the folder of model
    with open('static/pickle/'+str(station_id) + ".pkl", "rb") as handle:
        models[station_id] = pickle.load(handle)
    available_bikes_prediction = models[station_id].predict(f2).round()[0]
    return jsonify(bp=available_bikes_prediction)

if __name__ == "__main__":
    app.run(port=5001)





