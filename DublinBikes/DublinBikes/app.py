from flask import Flask, render_template, g, jsonify
import requests
import json
from sqlalchemy import create_engine
import pymysql



app = Flask(__name__)

def connect_to_database():
    with open('config.json', 'r') as f: #Open and read the configuration file
        config = json.load(f)       #creat a variable to store the loaded contians

    #variable for connecting to ysql
    #engine = create_engine('mysql+pymysql://scott:tiger@localhost/foo')

    engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(config['USER'],
                                                                   config['PASSWORD'],
                                                                   config['URI'],
                                                                   config['PORT'],
                                                                   config['DB']), echo=True)
    print("Connection successful")
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

@app.route("/stations")
def get_stations():
    engine = get_db()
    sql = "select * from STATION;"
    rows = engine.execute(sql).fetchall()
    print('#found {} stations', len(rows))
    # print(jsonify(stations=[dict(row.items()) for row in rows]))
    return jsonify(stations=[dict(row.items()) for row in rows])


# @app.route("/available/<int:station_id>")
# def get_stations(station_id):
#     engine = get_db()
#     data = []
#     sql = "SELECT available_bikes from stations where number ={};”.format(station_id)"
#     rows = engine.execute(sql)
#     for row in rows:
#     data.append(dict(row))
#
#     return jsonify(available=data)

@app.route('/')
# def index():
#
#     '''Loads index page'''
#
#     print(keyring.getWeatherKey())
#     return render_template("index.html", key = keyring.getMapKey(), a = keyring.getWeatherKey() )

@app.route('/index')
def map():
    return render_template('GoogleMap.html')


if __name__ == '__main__':
    app.run(debug = True)


# APIKEY = '5979ce80578015211c5630d5d3762548e5eba68d'
# NAME = "Dublin"
# STATIONS_URI = "https://api.jcdecaux.com/vls/v1/stations"
# r = requests.get(STATIONS_URI, params={"apiKey": APIKEY, "contract": NAME})
# stations = (json.loads(r.text))
# for station in stations:
#     for i in range(0,len(stations)):
#         print(stations[i]['address'])

