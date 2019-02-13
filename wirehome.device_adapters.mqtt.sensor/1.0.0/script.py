config = {}


def process_adapter_message(properties):
    type = properties.get("type", None)

    if type == "initialize":
        return __initialize__()

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def __initialize__():
    subscription_uid = "wirehome.mqtt.sensor:" + wirehome.context["component_uid"]
    topic = config["topic"]
    wirehome.mqtt.subscribe(subscription_uid, topic, __handle_mqtt_message__)


def __handle_mqtt_message__(properties):
    payload = properties["payload"]
    payload_string = wirehome.convert.to_string(payload)

    properties = {
        "type": "value_updated",
        "value": payload_string,
        "value_type": "string"
    }

    wirehome.publish_adapter_message(properties)
