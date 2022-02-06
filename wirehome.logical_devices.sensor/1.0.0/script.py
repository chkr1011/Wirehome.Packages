import datetime

wirehome = {}
config = {}


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
    type = message.get("type", None)

    if type == "value_updated":
        value = message.get("value", None)
        value_type = message.get("value_type", None)

        if value_type == "string":
            value = float(value)

        __set_sensor_value__(value)

        global_variable = config.get("publish_as_global_variable", None)
        if global_variable != None:
            wirehome.global_variables.set(global_variable, value)

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


def __set_sensor_value__(value):
    wirehome.component.set_status("last_update", datetime.datetime.now().isoformat())

    sensor_type = config.get("sensor_type", None)
    correction_value = config.get("correction_value", 0.0)
    
    if type(value) == float:
        value = value + correction_value
   
    if sensor_type == "temperature":
        wirehome.component.set_status("temperature.value", value)
    elif sensor_type == "humidity":
        wirehome.component.set_status("humidity.value", value)
    elif sensor_type == "pressure":
        wirehome.component.set_status("pressure.value", value)
    elif sensor_type == "custom":
        wirehome.component.set_status("sensor.value", value)

    __start_outdated_countdown__()
    wirehome.component.set_status("status.is_outdated", False)

    # Store the value so that it will be loaded after startup etc.
    #wirehome.value_storage.write(__get_value_storage_path__(), value)
