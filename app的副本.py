#!/usr/bin/env python
from flask import Flask, render_template, g, jsonify
import requests
import json
from sqlalchemy import create_engine
import pymysql

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


@app.route("/stations")
def get_stations():
    engine = get_db()
    sql = "select * from STATIONS;"
    rows = engine.execute(sql).fetchall()
    print('#found {} stations', len(rows))

    stations = jsonify(stations=[dict(row.items()) for row in rows])
    return stations



@app.route("/availability")
def get_availability():
    engine = get_db()
    sql = "SELECT * from STATION;"
    rows = engine.execute(sql).fetchall()
    print("#found {} availability", len(rows))
    avalibility = jsonify(availability=[dict(row) for row in rows])
    return avalibility


if __name__ == "__main__":
    app.run(debug=True)





