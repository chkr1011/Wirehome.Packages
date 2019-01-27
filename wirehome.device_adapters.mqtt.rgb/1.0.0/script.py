config = {}


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()
    elif type == "set_state":
        return __set_state__(message)

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def __initialize__():
    return {
        "type": "success",
        "supports_brightness": True,
        "supports_color": True
    }


def __set_state__(message):
    power_state = message.get("power_state", "off")
    brightness = message.get("brightness", 100)
    color = message.get("color", "#ffffff")

    if power_state != "on":
        mqtt_message = config.get("turn_off_message", None)
        topic = mqtt_message.get("topic", None)
        payload = mqtt_message.get("payload", None)

        __send_mqtt_message__(topic, payload)
        return {"type": "success"}

    max_pwm_value = config.get("max_pwm_value", 255)
    mqtt_message = config.get("set_color_message", None)
    topic = mqtt_message.get("topic", None)
    payload = mqtt_message.get("payload_template", None)

    # Convert HEX to RGB
    hex = color.lstrip("#")
    r, g, b = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

    # Apply brightness to RGB
    r = r * (brightness / 100)
    g = g * (brightness / 100)
    b = b * (brightness / 100)

    payload = payload.replace("{r}", str(absolute_value(r, max_pwm_value)))
    payload = payload.replace("{g}", str(absolute_value(g, max_pwm_value)))
    payload = payload.replace("{b}", str(absolute_value(b, max_pwm_value)))

    return __send_mqtt_message__(topic, payload)


def __send_mqtt_message__(topic, payload):
    parameters = {
        "topic": topic,
        "payload": payload
    }

    # Inspect response when RPC is available.
    # Or wait for special message.
    wirehome.mqtt.publish(parameters)

    return {"type": "success"}


def absolute_value(value, max_value):
    if value <= 0:
        return 0

    if value >= 255:
        return max_value

    result = (value / 255.0) * max_value
    return int(result)
