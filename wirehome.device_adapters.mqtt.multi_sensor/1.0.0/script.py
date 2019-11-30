config = {}


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()

    return wirehome.response_creator.not_supported(type)


def __initialize__():
    for key in config:
        subscription_uid = "wirehome.mqtt.multi_sensor/" + wirehome.context["component_uid"] + "/" + key

        subscription = config.get(key)
        topic = subscription["topic"]

        def f(m, k=key): __handle_mqtt_message__(k, m)
        wirehome.mqtt.subscribe(subscription_uid, topic, f)


def __handle_mqtt_message__(key, mqtt_message):
    payload = mqtt_message["payload"]
    payload_string = wirehome.convert.to_string(payload)

    wirehome.log.debug("Multi sensor received value (Key = {key}, Payload = {payload}).".format(key=key, payload=payload_string))

    adapter_message = {
        "type": "value_received",
        "key": key,
        "value": payload_string,
        "value_type": "string"
    }

    wirehome.publish_adapter_message(adapter_message)
