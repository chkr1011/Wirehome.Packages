def process_adapter_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()
    elif type == "turn_on":
        return __set_state_internal__("on")
    elif type == "turn_off":
        return __set_state_internal__("off")
    elif type == "set_state":
        return __set_state__(message)
    else:
        return {
            "type": "exception.not_supported",
            "origin_type": type
        }


def __initialize__():
    global _subscriptions
    _subscriptions = []

    backward_channel = config.get("backward_channel", None)
    if backward_channel == None:
        return

    component_uid = context["component_uid"]

    on_topic = backward_channel["on"]["topic"]
    subscription_uid = component_uid + "->wirehome.mqtt.relay.backward_channel.on"
    wirehome.mqtt.subscribe(subscription_uid, on_topic, __handle_backward_channel_message__)

    off_topic = backward_channel["off"]["topic"]
    if off_topic != on_topic:
        subscription_uid = component_uid + "->wirehome.mqtt.relay.backward_channel.off"
        wirehome.mqtt.subscribe(subscription_uid, off_topic, __handle_backward_channel_message__)

    return wirehome.response_creator.success()


def __destroy__():
    global _subscriptions

    for subscription_uid in _subscriptions:
        wirehome.mqtt.unsubscribe(subscription_uid)

    _subscriptions = []

    return wirehome.response_creator.success()


def __set_state__(message):
    power_state = message.get("power_state", None)
    if power_state == None:
        return {"type", "exception.parameter_missing"}

    if power_state == "on":
        __set_state_internal__("on")
    else:
        __set_state_internal__("off")


def __set_state_internal__(state):
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
        wirehome.mqtt.publish_external(parameters)
    else:
        wirehome.mqtt.publish(parameters)

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

    payload = wirehome.convert.to_string(message.get("payload", ""))
    filter_payload = wirehome.convert.to_string(filter.get("payload", ""))

    return payload == filter_payload
