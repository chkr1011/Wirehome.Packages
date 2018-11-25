def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def __initialize__(message):
    __set_sensor_value__("unknown")
    component.set_status("status.is_outdated", True)
    component.set_configuration("app.view_source", wirehome.package_manager.get_file_uri(scope["logic_uid"], "appView.html"))

    return publish_adapter_message({
        "type": "initialize"
    })


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "value_updated":
        value = message.get("value", None)
        value_type = message.get("value_type", None)

        if value_type == "string":
            value = convert.to_double(value)

        __set_sensor_value__(value)

        global_variable = config.get("publish_as_global_variable", None)
        if global_variable != None:
            global_variables.set(global_variable, value)

        return {
            "type": "success"
        }

    return {
        "type": "not_supported",
        "origin_type": type
    }


def __start_outdated_countdown__():
    uid = "wirehome.sensor.countdown.outdated:" + scope["component_uid"]
    timeout = config.get("outdated_timeout", 60000)
    scheduler.start_countdown(uid, timeout, __on_outdated_countdown_callback__)


def __on_outdated_countdown_callback__(_):
    component.set_status("status.is_outdated", True)


def __set_sensor_value__(value):
    sensor_type = config.get("sensor_type", None)

    if sensor_type == "temperature":
        component.set_status("temperature.value", value)
    elif sensor_type == "humidity":
        component.set_status("humidity.value", value)

    component.set_status("status.is_outdated", False)
    __start_outdated_countdown__()
