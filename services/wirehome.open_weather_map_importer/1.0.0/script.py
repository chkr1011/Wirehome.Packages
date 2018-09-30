from time import sleep


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
    function_pool.register("open_map_importer.test", __test__)


def stop():
    global is_running
    is_running = False


def get_status():
    return {
        "is_running": is_running
    }


def __poll_status__():
    while is_running == True:
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

        http_result = http_client.send(parameters)

        if http_result["status_code"] == 200:
            # print(uri)

            global status
            status.temperature = http_result["content"]["main"]["temp"]
            status.humidity = http_result["content"]["main"]["humidity"]
            status.sunrise = date_time_parser.file_time_to_local_time(http_result["content"]["sys"]["sunrise"])
            status.sunset = date_time_parser.file_time_to_local_time(http_result["content"]["sys"]["sunset"])
            status.condition = http_result["content"]["weather"][0]["main"]

            conditionIcon = http_result["content"]["weather"][0]["icon"]
            conditionIcon = "http://openweathermap.org/img/w/" + conditionIcon + ".png"

            global_variables.set("outdoor.temperature", status.temperature)
            global_variables.set("outdoor.humidity", status.temperature)
            global_variables.set("outdoor.sunrise", status.sunrise)
            global_variables.set("outdoor.sunset", status.sunset)

            global_variables.set("outdoor.condition", status.condition)
            global_variables.set("outdoor.condition.image_url", conditionIcon)

            global_variables.set("open_weahter_map.condition_code", http_result["content"]["weather"][0]["id"])

        sleep(update_interval)

def __test__(parameter):
    name = parameter.get("name", "niemand")
    return {
        "message": "hello " + name
    }