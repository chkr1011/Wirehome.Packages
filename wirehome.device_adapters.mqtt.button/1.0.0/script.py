config = {}


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

    subscription_uid = "wirehome.mqtt.button:" + wirehome.context["component_uid"]
    wirehome.mqtt.subscribe(subscription_uid, topic, __handle_mqtt_message__)

    return {"type": "success"}


def __handle_mqtt_message__(mqtt_message):
    payload = mqtt_message["payload"]

    message = {
        "type": "state_changed",
        "new_state": __transform_state__(payload)
    }

    wirehome.publish_adapter_message(message)


def __transform_state__(payload):
    payload_string = wirehome.convert.to_string(payload)

    if payload_string == "pressed" or payload_string == "True" or payload_string == "true" or payload_string == "1":
        return "pressed"

    if payload_string == "released" or payload_string == "False" or payload_string == "false" or payload_string == "0":
        return "released"

    value = wirehome.convert.list_to_ulong(payload)

    if value > 0:
        return "pressed"

    return "released"
