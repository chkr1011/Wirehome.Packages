def process_adapter_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()
    elif type == "turn_off":
        return __turn_off__()
    elif type == "set_color":
        return __set_color__(message)

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

def __set_color__(message):
    r = message["r"]
    g = message["g"]
    b = message["b"]

    max_pwm_value = config.get("max_pwm_value", 255)

    set_color_message = config.get("set_color_message", None)
    topic = set_color_message["topic"]
    payload = set_color_message.get("payload_template", "")
    payload = payload.replace("{r}", str(absolute_value(r, max_pwm_value)))
    payload = payload.replace("{g}", str(absolute_value(g, max_pwm_value)))
    payload = payload.replace("{b}", str(absolute_value(b, max_pwm_value)))

    return __send_mqtt_message__(topic, payload)


def __turn_off__():
    turn_off_message = config.get("turn_off_message", None)
    if turn_off_message != None:
        topic = turn_off_message["topic"]
        payload = turn_off_message.get("payload", "")

        return __send_mqtt_message__(topic, payload)

    return __set_color__({
        "r": 0,
        "g": 0,
        "b": 0
    })


def __send_mqtt_message__(topic, payload):
    parameters = {
        "topic": topic,
        "payload": payload
    }

    # Inspect response when RPC is available.
    # Or wait for special message.
    mqtt.publish(parameters)

    return {"type": "success"}


def absolute_value(value, max_value):
    if value <= 0:
        return 0

    if value >= 255:
        return max_value

    result = (value / 255.0) * max_value
    return int(result)
