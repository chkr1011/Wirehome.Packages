def process_adapter_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def __initialize__():
    topic = config["topic"]

    subscription_uid = "wirehome.mqtt.button:" + scope["component_uid"]
    mqtt.subscribe(subscription_uid, topic, __handle_mqtt_message__)

    return {"type": "success"}


def __handle_mqtt_message__(mqtt_message):
    payload = mqtt_message["payload"]
    payload_string = convert.to_string(payload)

    message = {
        "type": "state_changed",
        "new_state": payload_string
    }

    publish_adapter_message(message)
