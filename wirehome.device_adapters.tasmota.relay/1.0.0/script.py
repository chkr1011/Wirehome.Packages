config = {}


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()
    elif type == "turn_on":
        return __set_state__("on")
    elif type == "turn_off":
        return __set_state__("off")
    else:
        return {
            "type": "exception.not_supported",
            "origin_type": type
        }


def __initialize__():
    device_uid = config["device_uid"]
    supports_power_consumption = config.get("supports_power_consumption", False)

    if supports_power_consumption:
        subscription_uid = "wirehome.tasmota.relay.ps:" + wirehome.context["component_uid"]

        wirehome.mqtt.subscribe(subscription_uid, "stat/" + device_uid + "/STATUS8", __power_consumption_received__)

        update_interval = config.get("power_consumption_update_interval", 5000)
        timer_uid = "wirehome.tasmota.relay.pc.timer." + device_uid
        wirehome.scheduler.start_timer(timer_uid, update_interval, __request_power_consumption__)

    subscription_uid = "wirehome.tasmota.relay.stat:" + wirehome.context["component_uid"]
    topic = "stat/" + device_uid + "/POWER"
    wirehome.mqtt.subscribe(subscription_uid, topic, __handle_mqtt_message__)

    return {"type": "success"}


def __set_state__(state):
    device_uid = config["device_uid"]

    parameters = {
        "topic": "cmnd/" + device_uid + "/power",
        "payload": state,
        "retain": False
    }

    wirehome.mqtt.publish(parameters)

    return {"type": "success"}


def __handle_mqtt_message__(properties):
    payload = properties["payload"]
    payload_string = wirehome.convert.to_string(payload)

    type = ""
    if payload_string == "OFF":
        type = "turned_off"
    elif payload_string == "ON":
        type = "turned_on"

    properties = {"type": type}

    publish_adapter_message(properties)


def __request_power_consumption__(parameters):
    device_uid = config["device_uid"]

    parameters = {
        "topic": "cmnd/" + device_uid + "/status",
        "payload": "8",
        "retain": False
    }

    wirehome.mqtt.publish(parameters)


def __power_consumption_received__(message):
    payload = message.get("payload", None)
    json = wirehome.json_serializer.deserialize(payload)

    if "StatusSNS" in json:
        if "ENERGY" in json["StatusSNS"]:
            if "Power" in json["StatusSNS"]["ENERGY"]:
                consumption = json["StatusSNS"]["ENERGY"]["Power"]
                wirehome.component.set_status("power.consumption", consumption)
