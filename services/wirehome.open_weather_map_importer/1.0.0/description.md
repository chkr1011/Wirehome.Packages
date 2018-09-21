# Summary

This service loads weather data from _Open Weather Map_ (an account is required) and forwards the data to global variables. The following global variables are set.

* `outdoor.temperature`
* `outdoor.humidity`
* `outdoor.sunrise`
* `outdoor.sunset`
* `outdoor.condition`
* `outdoor.condition.image_url`
* `open_weather_map.condition_code`

# Parameters

The service requires the following parameters.


## Mandatory parameters

The following parameters are required for every kind of query.

```json
{
    "config": 
    {
        "app_id": "xyz", // The APP ID from the _Open Weather Map_ portal (account required).
        "update_interval": 60 // Seconds (60 is default)
    }
}
```


## Query by city

The following parameters are required for a query by a city name.

```json
{
    "config":
    {
        "query_mode": "city",
        "city_name": "Kamp-Lintfort"
    }
}
```


## Query by coordinates

The following parameters are required for a query by it's coordinates.

```json
{
    "config":
    {
        "query_mode": "coordinates",
        "latitude": 51.11893,
        "longitude": 6.53095
    }
}
```