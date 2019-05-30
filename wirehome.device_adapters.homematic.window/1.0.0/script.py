SERVICE_ID = "wirehome.services.homematic.ccu"

config = {}


def process_adapter_message(message):
    message_type = message.get("type", None)

    if message_type == "initialize":
        return __initialize__()
    if message_type == "destroy":
        return __destroy__()
    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def __initialize__():
    result = {"type": "success"}

    global subscription_uid
    subscription_uid = wirehome.context["component_uid"] + "->homematic.ccu.event.device_state_changed"

    address = config.get("address")
    property_name = config.get("property", "STATE")

    subscription_filter = {
        "type": "homematic.ccu.event.device_state_changed",
        "address": address,
        "property": property_name
    }

    wirehome.message_bus.subscribe(subscription_uid, subscription_filter, __gateway_manager_callback__)

    initial_value = wirehome.services.invoke(SERVICE_ID, "get_device_value", address, property_name)
    __update_value(initial_value)

    return result


def __destroy__():
    wirehome.message_bus.unsubscribe(subscription_uid)


def __gateway_manager_callback__(message):
    new_value = message.get("new", None)

    __update_value(new_value)


def __update_value(new_value):
    new_state = ""

    if new_value == 1:
        new_state = "open"
    elif new_value == 0:
        new_state = "closed"

    wirehome.publish_adapter_message({
        "type": "state_changed",
        "new_state": new_state
    })
