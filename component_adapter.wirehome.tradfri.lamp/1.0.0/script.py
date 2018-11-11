SERVICE_ID = "service.wirehome.tradfri.gateway_manager"


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()
    if type == "destroy":
        return __destroy__()
    if type == "set_state":
        return __set_state__(message)
    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def __initialize__():
    result = {"type": "success"}
    result["supports_brightness"] = True
    result["supports_color"] = False

    global subscription_uid
    subscription_uid = context["component_uid"] + "->tradfri.gateway_manager.event.device_state_changed"

    filter = {
        "type": "tradfri.gateway_manager.event.device_state_changed"
    }

    wirehome.message_bus.subscribe(subscription_uid, filter, __gateway_manager_callback__)

    return result


def __destroy__():
    wirehome.message_bus.unsubscribe(subscription_uid)


def __set_state__(message):
    parameters = {
        "device_id": config.get("device_id", None),
        "device_caption": config.get("device_caption", None)
    }

    if message.get("power_state", None) == "on":
        parameters["power_state"] = 1
    else:
        parameters["power_state"] = 0

    brightness = message.get("brightness", None)
    if brightness != None:
        parameters["brightness"] = int((brightness / 100.0) * 245)

    color = message.get("color", None)
    if color != None:
        parameters["color"] = color

    return wirehome.services.invoke(SERVICE_ID, "set_device_status", parameters)


def __gateway_manager_callback__(message):
    own_device_id = config.get("device_id", None)
    message_device_id = message.get("device_id", None)

    if message_device_id != own_device_id:
        return

    property = message.get("property", None)

    if property == "power_state":
        new_state = message.get("new_state", None)

        publish_adapter_message({
            "type": "power_state_changed",
            "power_state":  new_state
        })
