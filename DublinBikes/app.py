#!/usr/bin/env python
from flask import Flask, render_template, g, jsonify, request
import requests
import json
from sqlalchemy import create_engine
import pymysql
import time


# Create our flask app. Static files are served from 'static' directory
app = Flask(__name__, static_url_path='')
app.config.from_object('config')


# this route simply serves 'static/index.html'
@app.route('/')
def root():
    return render_template('index.html')


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
    db = getattr(g, '_database', None)
    if db is None:
        db = connect_to_database()
        g.__database = db
    print("Database connected")
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/dynamic_stations")
def dynamic_stations():
    APIKEY = '5979ce80578015211c5630d5d3762548e5eba68d'
    NAME = "Dublin"
    STATIONS_URI = "https://api.jcdecaux.com/vls/v1/stations"
    temp = requests.get(STATIONS_URI, params={"apiKey": APIKEY, "contract": NAME})
    stations_detail = json.loads(temp.text)
    return jsonify(stations=stations_detail)



# @app.route("/stations")
# def get_stations():
#     engine = get_db()
#     sql = "select * from STATIONS;"
#     rows = engine.execute(sql).fetchall()
#     print('#found {} stations', len(rows))
#
#     stations = jsonify(stations=[dict(row.items()) for row in rows])
#     return stations


# @app.route("/occupancy/<int:station_id>")
# def get_occupancy(station_id):
#     engine = get_db()
#     data = []
#     sql = "SELECT available_bikes, available_bike_stands FROM STATION where number={};".format(station_id)
#     details = engine.execute(sql).fetchall()
#     for row in details:
#         data.append(dict(row))
#     return jsonify(occupancy=data)


@app.route("/daily/<int:station_id>")
def week_chart(station_id):
    engine = get_db()
    sql = "SELECT available_bikes, available_bike_stands, last_update FROM STATION where number={};".format(station_id)
    rows = engine.execute(sql).fetchall()
    week_average_bikes = []
    week_average_stands = []
    days = [0, 1, 2, 3, 4, 5, 6]
    for day in days:
        week_average_bikes.append(day_avg(rows, day)[0])
        week_average_stands.append(day_avg(rows, day)[1])
    daily = jsonify(week_average_bikes=week_average_bikes, week_average_stands=week_average_stands)
    return daily


def day_avg(rows, day):
    available_bikes = []
    available_bike_stands = []
    for row in rows:
        unix_stamp = time.localtime(int(row["last_update"]))
        weekday = int(time.strftime("%w", unix_stamp))
        if weekday == day:
            available_bikes.append(row["available_bikes"])
            available_bike_stands.append(row["available_bike_stands"])
    day_avg_bikes = int(round((sum(available_bikes) / len(available_bikes)), 0))
    day_avg_bike_stands = int(round((sum(available_bike_stands) / len(available_bike_stands)), 0))
    return day_avg_bikes, day_avg_bike_stands


# @app.route("/hourly/<int:station_id>")
# def week_chart(station_id):
#     engine = get_db()
#     sql = "SELECT available_bikes, available_bike_stands, last_update FROM STATION where number={},;".format(station_id)
#     rows = engine.execute(sql).fetchall()



if __name__ == "__main__":
    app.run(debug=True)





