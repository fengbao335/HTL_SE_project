
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
    $.getJSON('http://127.0.0.1:5000/dynamic_stations', null, function (data) {
        var stations = data.stations;
        $.each(stations, function (i,station) {
            var marker = new google.maps.Marker({
                position: {
                    lat: station.position.lat,
                    lng: station.position.lng
                },
                map: map,
                title: station.name,
                number: station.number
            });
            marker.metadata = {type: "point", id: station.number};
            google.maps.event.addListener(marker, 'click', (function(marker, stations) {
                return function() {
                    if (station.banking == 1) {
                        station.banking = "Yes";
                    } else {
                        station.banking = "No";
                    }
                    var number = station.number;
                    var content = "Station name: " + station.name + "<br><br>" + "Banking: " + station.banking + "<br><br>" + "Available Bikes: " + station.available_bikes + "<br><br>" + "Available Bike Stands: " + station.available_bike_stands + "<br><br>" + "Status: " + station.status + "<br>";
                    var button = "<button onclick='daily_chart(" + number + ")'>Show Daily Chart</button>";
                    infoWindow.setContent(content + "<br> " + button);
                    infoWindow.open(map, marker);
                }
            })(marker, stations));
        });
    });
}



