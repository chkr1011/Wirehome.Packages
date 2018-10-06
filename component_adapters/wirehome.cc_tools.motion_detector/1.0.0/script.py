SERVICE_ID = "wirehome.cc_tools.board_manager"


def process_adapter_message(message):
    if message["type"] == "initialize":
        return __initialize__()

    return {
        "type": "not_implemented"
    }


def __initialize__():
    filter = {
        "type": "cc_tools.board_manager.event.state_changed",
        "device_uid": config["device_uid"]
    }

    message_bus.subscribe(filter, __state_changed_callback__)

    __publish_state__()


def __publish_state__():
    service_parameters = {
        "device_uid": config["device_uid"],
        "port": config["port"]
    }

    service_result = services.invoke(SERVICE_ID, "get_state", service_parameters)

    state = service_result["pin_state"]
    is_inverted = config.get("is_inverted", False)

    motion_detection_state = "idle"

    if is_inverted == True and state == "low":
        motion_detection_state = "detected"
    elif is_inverted == False and state == "high":
        motion_detection_state = "detected"

    message = {
        "type": "state_changed",
        "new_state": motion_detection_state
    }

    publish_adapter_message(message)


def __state_changed_callback__(properties):
    __publish_state__()
