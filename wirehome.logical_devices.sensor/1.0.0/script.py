import datetime

wirehome = {}
config = {}

current_value = 0.0

def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def __initialize__(message):
    #value_storage_path = __get_value_storage_path__()
    #value = wirehome.value_storage.read(value_storage_path, "unknown")
    #__set_sensor_value__(value)

    __set_sensor_value__("unknown")

    wirehome.component.set_status("status.is_outdated", True)
    wirehome.component.set_configuration("app.view_source", wirehome.package_manager.get_file_uri(wirehome.context["logic_uid"], "appView.html"))

    return wirehome.publish_adapter_message({
        "type": "initialize"
    })


def process_adapter_message(message):
    global current_value

    type = message.get("type", None)

    if type == "value_updated":
        new_value = message.get("value", None)
        value_type = message.get("value_type", None)

        # Convert value
        if value_type == "string":
            new_value = float(new_value)

        # Increase or decrease value
        correction_value = config.get("correction_value", 0.0)
        new_value = new_value + correction_value

        # Round value
        value_round_digits = 1
        sensor_type = config.get("sensor_type", None)
        if sensor_type == "humidity":
            value_round_digits = 0
        elif sensor_type == "pressure":
            value_round_digits = 0

        value_round_digits = config.get("value_round_digits", value_round_digits)
        new_value = round(new_value, value_round_digits)      

        # Apply new value.
        __set_sensor_value__(new_value)

        global_variable = config.get("publish_as_global_variable", None)
        if global_variable != None:
            wirehome.global_variables.set(global_variable, new_value)

        return {
            "type": "success"
        }

    return {
        "type": "not_supported",
        "origin_type": type
    }


def __start_outdated_countdown__():
    uid = "wirehome.sensor.countdown.outdated:" + wirehome.context["component_uid"]
    timeout = config.get("outdated_timeout", 150000) # 2,5 minutes are used as timeout
    wirehome.scheduler.start_countdown(uid, timeout, __on_outdated_countdown_callback__)


def __on_outdated_countdown_callback__(_):
    wirehome.component.set_status("status.is_outdated", True)


def __get_value_storage_path__():
    component_uid = wirehome.context["component_uid"]
    return "{component_uid}/value".format(component_uid=component_uid)


def __set_sensor_value__(new_value):
    sensor_type = config.get("sensor_type", None)
       
    if sensor_type == "temperature":
        wirehome.component.set_status("temperature.value", new_value)
    elif sensor_type == "humidity":
        wirehome.component.set_status("humidity.value", new_value)
    elif sensor_type == "pressure":
        wirehome.component.set_status("pressure.value", new_value)
    elif sensor_type == "custom":
        wirehome.component.set_status("sensor.value", new_value)

    __start_outdated_countdown__()
    wirehome.component.set_status("status.is_outdated", False)

    wirehome.component.set_status("last_update", datetime.datetime.now().isoformat())

    # Store the value so that it will be loaded after startup etc.
    #wirehome.value_storage.write(__get_value_storage_path__(), value)
