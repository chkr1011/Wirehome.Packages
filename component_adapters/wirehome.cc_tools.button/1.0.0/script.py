SERVICE_ID = "wirehome.cc_tools.board_manager"


def process_adapter_message(message):
    type = message.get("type", None)
    if type == "initialize":
        return __initialize__()

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def __initialize__():
    filter = {
        "type": "cc_tools.board_manager.event.state_changed",
        "device_uid": config["device_uid"]
    }

    uid = "wirehome.cc_tools.state_changed:" + scope["component_uid"]
    message_bus.subscribe(uid, filter, __state_changed_callback__)

    __publish_state__()


def __publish_state__():
    service_parameters = {
        "device_uid": config["device_uid"],
        "port":  config["port"]
    }

    service_result = services.invoke(SERVICE_ID, "get_state", service_parameters)
    state = service_result["pin_state"]

    is_inverted = config.get("is_inverted", True)

    button_state = "released"

    if is_inverted == True and state == "low":
        button_state = "pressed"
    elif is_inverted == False and state == "high":
        button_state = "pressed"

    message = {
        "type": "state_changed",
        "new_state": button_state
    }

    publish_adapter_message(message)


def __state_changed_callback__(properties):
    __publish_state__()
