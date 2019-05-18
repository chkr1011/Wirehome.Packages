config = {}


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()

    return wirehome.response_creator.not_supported(type)


def __initialize__():
    subscription_uid = "wirehome.mqtt.sensor/" + wirehome.context["component_uid"]
    topic = config["topic"]
    wirehome.mqtt.subscribe(subscription_uid, topic, __handle_mqtt_message__)


def __handle_mqtt_message__(mqtt_message):
    payload = mqtt_message["payload"]
    payload_string = wirehome.convert.to_string(payload)

    adapter_message = {
        "type": "value_updated",
        "value": payload_string,
        "value_type": "string"
    }

    wirehome.publish_adapter_message(adapter_message)
