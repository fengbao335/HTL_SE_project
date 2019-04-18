#!/usr/bin/env python
from flask import Flask, render_template, g, jsonify, request
import requests
import json
from sqlalchemy import create_engine
import pymysql
import time
import pandas as pd
import numpy as np
import pickle


# Create our flask app. Static files are served from 'static' directory
app = Flask(__name__, static_url_path='')
app.config.from_object('config')


# this route simply serves 'static/index.html'
@app.route('/')
@app.route('/index')
def root():
    return render_template('index.html')


@app.route('/predict_forecast')
def page2():
    return render_template('predict_forecast.html')


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
    """把从数据库抓取的数据存到变量db里"""
    db = getattr(g, '_database', None)
    if db is None:
        db = connect_to_database()
        g.__database = db
    print("Database connected")
    return db


@app.teardown_appcontext
def close_connection(exception):
    """关闭和数据库的连接"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/dynamic_stations")
def dynamic_stations():

    """用JCDecaux的API抓取数据，以json的形式发送到页面：dynamic_stations"""

    APIKEY = '5979ce80578015211c5630d5d3762548e5eba68d'  #JCDecaux 的 API
    NAME = "Dublin"
    STATIONS_URI = "https://api.jcdecaux.com/vls/v1/stations"
    temp = requests.get(STATIONS_URI, params={"apiKey": APIKEY, "contract": NAME})
    stations_detail = json.loads(temp.text)
    return jsonify(stations=stations_detail)


@app.route("/daily/<int:station_id>")
def week_chart(station_id):
    """这个函数用来把参数对应的站点一周中平均每天的occupancy发送到对应的URL"""
    engine = get_db()
    #根据传入的参数station_id，从数据库挑选出相应站点的occupancy
    sql = "SELECT available_bikes, available_bike_stands, last_update FROM STATION where number={};".format(station_id)
    rows = engine.execute(sql).fetchall()
    week_average_bikes = []
    week_average_stands = []
    # 列表day中数值0-6代表周日到周六
    days = [0, 1, 2, 3, 4, 5, 6]
    for day in days:
        #调用day_avg函数，计算每一天的occupancy的平均值，然后添加到列表中
        week_average_bikes.append(day_avg(rows, day)[0])
        week_average_stands.append(day_avg(rows, day)[1])
    daily = jsonify(week_average_bikes=week_average_bikes, week_average_stands=week_average_stands)
    return daily


def day_avg(rows, day):
    """这个函数用来计算每一天的occupancy的平均值"""
    available_bikes = []
    available_bike_stands = []
    for row in rows:
        # 把unix stamp 转换成数字0-6，分别代表周日到周六
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
    f2 = pd.DataFrame(np.array([station_id,time_hour, temp, wind, weather_Drizzle, weather_Rain])).T
    models = {}
    with open('static/pickle/'+str(station_id) + ".pkl", "rb") as handle:
        models[station_id] = pickle.load(handle)
    available_bikes_prediction = models[station_id].predict(f2).round()[0]
    return jsonify(bp=available_bikes_prediction)


if __name__ == "__main__":
    app.run(debug=True)





