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
    mqtt.subscribe(topic, __handle_mqtt_message__)


def __handle_mqtt_message__(properties):
    payload = properties["payload"]
    payload_string = convert.to_string(payload)

    properties = {
        "type": "value_updated",
        "value": payload_string,
        "value_type": "string"
    }

    publish_adapter_message(properties)
