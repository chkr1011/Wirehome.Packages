def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)

    return {
        "type": "exception.not_supported"
    }


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "value_updated":
        value = message.get("value", None)
        value_type = message.get("value_type", None)

        if value_type == "string":
            value = convert.to_double(value)

        sensor_type = config.get("sensor_type", None)

        if sensor_type == "temperature":
            component.set_status("temperature.value", value)
        elif sensor_type == "humidity":
            component.set_status("humidity.value", value)

        return {
            "type": "success"
        }

    return {
        "type": "not_supported"
    }


def __initialize__(message):
    sensor_type = config.get("sensor_type", None)
    
    if sensor_type == "temperature":
        component.set_status("temperature.value", "unknown")
    elif sensor_type == "humidity":
        component.set_status("humidity.value", "unknown")

    return publish_adapter_message({
        "type": "initialize"
    })
