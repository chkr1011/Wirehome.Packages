import time

class Status:
    sunrise = None
    sunset = None
    temperature = None
    humidity = None
    condition = None


def initialize():
    pass


def start():
    global status, is_running
    status = Status()
    is_running = True

    scheduler.start_thread("wirehome.open_weather_map_importer.poll_thread", __poll_status__)


def stop():
    global is_running
    is_running = False


def get_status():
    return {
        "is_running": is_running
    }


def __poll_status__(_):
    query_mode = config.get("query_mode", "city")
    app_id = config.get("app_id", None)
    update_interval = config.get("update_interval", 60)
    city = config.get("city_name", "")
    latitude = config.get("latitude", 0)
    longitude = config.get("longitude", 0)

    if query_mode == "city":
        uri = "http://api.openweathermap.org/data/2.5/weather?q=" + city
    else:
        uri = "http://api.openweathermap.org/data/2.5/weather?lat=" + str(latitude) + "&lon=" + str(longitude)

    uri += "&appid=" + app_id + "&units=metric"

    parameters = {
        "method": "get",
        "uri":  uri,
        "response_content_type": "json"
    }

    while is_running == True:
        http_result = http_client.send(parameters)

        if http_result.get("type", None) == "success" and http_result.get("status_code", -1) == 200:
            try:
                main = http_result["content"]["main"]
                sys = http_result["content"]["sys"]
                weather = http_result["content"]["weather"]

                global status
                status.temperature = main["temp"]
                status.humidity = main["humidity"]
                status.sunrise = time.strftime('%H:%M:%S', time.localtime(sys["sunrise"]))
                status.sunset = time.strftime('%H:%M:%S', time.localtime(sys["sunset"]))
                status.condition = weather[0]["main"]

                conditionIcon = weather[0]["icon"]
                conditionIcon = "https://openweathermap.org/img/w/" + conditionIcon + ".png"

                if config.get("import_temperature", True) == True:
                    global_variables.set("outdoor.temperature", status.temperature)

                if config.get("import_humidity", True) == True:
                    global_variables.set("outdoor.humidity", status.humidity)

                if config.get("import_sunrise", True) == True:
                    global_variables.set("outdoor.sunrise", status.sunrise)

                if config.get("import_sunset", True) == True:
                    global_variables.set("outdoor.sunset", status.sunset)

                global_variables.set("outdoor.condition", status.condition)
                global_variables.set("outdoor.condition.image_url", conditionIcon)

                global_variables.set("open_weather_map.condition_code", weather[0]["id"])
            except:
                log.error("Error while polling Open Weather Map data. " + sys.exc_info()[0])

        time.sleep(update_interval)
