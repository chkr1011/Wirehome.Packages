def process_adapter_message(message):
    type = message.get("type", None)

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
    backward_channel = config.get("backward_channel", None)
    if backward_channel == None:
        return

    component_uid = scope["component_uid"]
    on_topic = backward_channel["on"]["topic"]
    subscription_uid = "wirehome.mqtt.relay.backward_channel.on:" + component_uid
    mqtt.subscribe(subscription_uid, on_topic, __handle_backward_channel_message__)

    off_topic = backward_channel["off"]["topic"]
    if off_topic != on_topic:
        subscription_uid = "wirehome.mqtt.relay.backward_channel.off:" + component_uid
        mqtt.subscribe(subscription_uid, off_topic, __handle_backward_channel_message__)

    return {"type": "success"}


def __set_state__(state):
    if state == "on":
        message = config.get("on", {})
    else:
        message = config.get("off", {})

    parameters = {
        "topic": message.get("topic", None),
        "payload": message.get("payload", None)
    }

    server = message.get("server", None)
    if server != None:
        parameters["server"] = server
        mqtt.publish_external(parameters)
    else:
        mqtt.publish(parameters)

    result = {
        "type": "success"
    }

    if config.get("update_status_from_backward_channel_only", False) == True:
        result["skip_status_update"] = True

    return result


def __handle_backward_channel_message__(message):
    backward_channel = config.get("backward_channel", None)
    if backward_channel == None:
        return

    if __is_match__(message, backward_channel.get("on")):
        publish_adapter_message({
            "type": "power_state_changed",
            "power_state": "on"
        })
    elif __is_match__(message, backward_channel.get("off")):
        publish_adapter_message({
            "type": "power_state_changed",
            "power_state": "off"
        })


def __is_match__(message, filter):
    filter_topic = filter.get("topic")
    topic = message.get("topic")

    if topic != filter_topic:
        return False

    payload = convert.to_string(message.get("payload", ""))
    filter_payload = convert.to_string(filter.get("payload", ""))

    return payload == filter_payload
