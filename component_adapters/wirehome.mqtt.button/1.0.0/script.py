def process_adapter_message(properties):
    type = properties.get("type", None)

    if type == "initialize":
        return __initialize__()

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def __initialize__():
    topic = config["topic"]

    global subscription_uid
    subscription_uid = mqtt.subscribe(topic, __handle_mqtt_message__)

    return {"type": "success"}


def __handle_mqtt_message__(properties):
    payload = properties["payload"]
    payload_string = convert.to_string(payload)

    properties = {
        "type": "state_changed",
        "new_state": payload_string
    }

    adapter.publish_adapter_message(properties)
