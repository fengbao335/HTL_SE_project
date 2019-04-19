from flask import jsonify
import unittest
import requests
import json
import tempfile



class TestDynamic_Stitions(unittest.TestCase):
    def dynamic_stations(self):

        APIKEY = '5979ce80578015211c5630d5d3762548e5eba68d'
        NAME = "Dublin"
        STATIONS_URI = "https://api.jcdecaux.com/vls/v1/stations"
        temp = requests.get(STATIONS_URI, params={"apiKey": APIKEY, "contract": NAME})
        stations_detail = json.loads(temp.text)
        return jsonify(stations=stations_detail)


    def test_notnone(self):
        data = self.app.get('/')
        self.assertIsNotNone(data)

if __name__ == '__main__':
    unittest.main()
