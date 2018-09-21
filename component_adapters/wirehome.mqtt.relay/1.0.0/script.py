def process_adapter_message(properties):
    type = properties.get("type", None)

    if type == "initialize":
        return __initialize__()
    elif type == "turn_on":
        return __set_state__("on")
    elif type == "turn_off":
        return __set_state__("off")

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def __initialize__():
    return {"type": "success"}
    

def __set_state__(state):
    if state == "on":
        topic = config["on"]["topic"]
        payload = config["on"].get("payload", "on")
    else:
        topic = config["off"]["topic"]
        payload = config["off"].get("payload", "off")

    parameters = {
        "topic": topic,
        "payload": payload
    }

    mqtt.publish(parameters)

    return {"type": "success"}