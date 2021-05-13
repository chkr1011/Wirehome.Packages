import json


wirehome = {}
config = {}


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()
    else:
        return {
            "type": "exception.not_supported",
            "origin_type": type
        }


def __initialize__():
    component_uid = wirehome.context["component_uid"]

    device_uid = config["device_uid"]

    subscription_uid = "wirehome.tasmota.sensor.tele:{component_uid}".format(component_uid=component_uid)

    topic = "tele/" + device_uid + "/SENSOR"
    wirehome.mqtt.subscribe(subscription_uid, topic, __handle_mqtt_message__)

    return {"type": "success"}


def __handle_mqtt_message__(mqtt_message):
    sensor_uid = config.get("sensor_uid", None)
    value_uid = config.get("value_uid", "Temperature")

    payload = mqtt_message["payload"]
    payload_string = wirehome.convert.to_string(payload)
    document = json.loads(payload_string)

    value = document[sensor_uid][value_uid]

    logic_message = {
        "type": "value_updated",
        "value": value
    }

    wirehome.publish_adapter_message(logic_message)