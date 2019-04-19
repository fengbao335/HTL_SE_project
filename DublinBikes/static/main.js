function initMap() {
    // ROOT is the location of our flask app
    ROOT = window.location.origin;
    // radius units are metres
    radius = 23, zoom = 14;
    var centre = {
        lat: 53.346763,
        lng: -6.2568436
    };
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: zoom,
        center: centre
    });
    var infoWindow = new google.maps.InfoWindow();
    // get json data from /dynamic_stations URL
    $.getJSON('http://127.0.0.1:5000/dynamic_stations', null, function (data) {
        var stations = data.stations;
        $.each(stations, function (i,station) {
            // the marker color is depending on the occupancy
            if (20<=station.available_bikes) {
                var marker = new google.maps.Marker({
                position: {
                    lat: station.position.lat,
                    lng: station.position.lng
                },
                icon: {
                  url: "http://maps.google.com/mapfiles/ms/icons/green-dot.png"
                },
                map: map,
                title: station.name,
                number: station.number
            });
            }
            else if (station.available_bikes<=10) {
                var marker = new google.maps.Marker({
                position: {
                    lat: station.position.lat,
                    lng: station.position.lng
                },
                icon: {
                  url: "http://maps.google.com/mapfiles/ms/icons/red-dot.png"
                },
                map: map,
                title: station.name,
                number: station.number
            });
            }
            else {
                var marker = new google.maps.Marker({
                position: {
                    lat: station.position.lat,
                    lng: station.position.lng
                },
                icon: {
                  url: "http://maps.google.com/mapfiles/ms/icons/yellow-dot.png"
                },
                map: map,
                title: station.name,
                number: station.number
            });
            }
            marker.metadata = {type: "point", id: station.number};
            google.maps.event.addListener(marker, 'click', (function(marker, stations) {
                return function() {
                    if (station.banking == 1) {
                        station.banking = "Yes";
                    } else {
                        station.banking = "No";
                    }
                    let number = station.number;
                    let station_name = station.name;
                    let available_bikes = station.available_bikes;
                    let available_bike_stands = station.available_bike_stands;
                    let station_bank = station.banking;
                    let station_status = station.status;

                    // the following variable is the content of infoWindow
                    var content =
                        '<div id="info">\n' +
                        '        <p>Station name: '+ station_name +'</p>\n' +
                        '\n' +
                        '        <p>Available Bikes: '+ available_bikes +'</p>\n' +
                        '\n' +
                        '        <p>Available Bike Stands: '+ available_bike_stands +'</p>\n' +
                        '\n' +
                        '        <p>Banking: '+ station_bank +'</p>\n' +
                        '\n' +
                        '        <p>Status: '+ station_status +'</p>\n' +
                        '        <br>\n' +
                        '        <button id="info_btn" onclick=info_btn() style="display: inline">Current Information</button>\n' +
                        '        <button id="prediction_btn" onclick=prediction_btn() style="display: inline">Prediction</button>\n' +
                        '        <button id="chart_btn" onclick=daily_chart(' + number + ') style="display: inline">Show Week Chart</button>\n' +
                        '    </div>\n' +
                        '    <div id="prediction" style="display:none;">\n' +
                        '        <p>Please select a day within 3 days.</p>\n' +
                        '        <input type="date" name="date" id="prediction_date">\n' +
                        '        <select id="prediction_time">\n' +
                        '            <option value="00:00:00">00:00:00</option>\n' +
                        '            <option value="03:00:00">03:00:00</option>\n' +
                        '            <option value="06:00:00">06:00:00</option>\n' +
                        '            <option value="09:00:00">09:00:00</option>\n' +
                        '            <option value="12:00:00">12:00:00</option>\n' +
                        '            <option value="15:00:00">15:00:00</option>\n' +
                        '            <option value="18:00:00">18:00:00</option>\n' +
                        '            <option value="21:00:00">21:00:00</option>\n' +
                        '        </select>\n' +
                        '        <br><br>\n' +
                        '        <button onclick=show_forecast() type="button">Show Weather Forecast</button>\n' +
                        '        <br>\n' +
                        '        <div id="weather_prediction">\n' +
                        '        </div>\n' +
                        '        <br>\n' +
                        '        <button onclick=show_occupancy_prediction(' + number + ') type="button">Show Bikes Prediction</button>\n' +
                        '        <br>\n' +
                        '        <div id="occupancy_prediction">\n' +
                        '        </div>\n' +
                        '        <br>\n' +
                        '        <button id="info_btn" onclick=info_btn() style="display: inline">Current Information</button>\n' +
                        '        <button id="prediction_btn" onclick=prediction_btn() style="display: inline">Prediction</button>\n' +
                        '        <button id="chart_btn" onclick=daily_chart(' + number + ') style="display: inline">Show Week Chart</button>\n' +
                        '    </div>';
                    infoWindow.setContent(content);
                    infoWindow.open(map, marker);
                }
            })(marker, stations));
        });
    });
}

function prediction_btn() {
    document.getElementById('info').style.display = 'none';
    document.getElementById('prediction').style.display = 'block';
}
function info_btn() {
    document.getElementById('info').style.display = 'block';
    document.getElementById('prediction').style.display = 'none';
}

function show_forecast() {
    var date = document.getElementById("prediction_date").value;
    var time = document.getElementById("prediction_time").value;
    var show = document.getElementById("weather_prediction");
    $.getJSON('http://api.openweathermap.org/data/2.5/forecast?appid=9511c6f09bf671d3bd65bf650197234f&units=metric&q=Dublin', function(data) {
        var result = data.list;
        for (i = 0; i <
            result.length; i++) {
            var temp = result[i].main.temp;
            var weather = result[i].weather[0].main;
            var wind = result[i].wind.speed;
            var target = result[i].dt_txt;
            if (target == date + " " + time) {
                show.innerHTML = ("Weather: " + weather + " <br />" + "Temperture: " + temp + " °C" + "<br />" + "Wind Speed: " + wind + " m/s");
            }
        }
    });
}

function show_occupancy_prediction(number, time) {

    // get prediction data from URl
    var time = document.getElementById("prediction_time").value;
    var int_hour = Number(time.slice(0, 2));
    console.log(int_hour);
    $.getJSON("http://127.0.0.1:5000/bikes_prediction/" + number + "/" + int_hour, null, function(data) {
        var show = document.getElementById("occupancy_prediction");
        show.innerHTML = ("Available Bikes: " + data.bp);
    });
}

