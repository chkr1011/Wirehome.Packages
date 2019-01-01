SERVICE_ID = "wirehome.services.cc_tools.board_manager"

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
    filter = {
        "type": "cc_tools.board_manager.event.state_changed",
        "device_uid": config["device_uid"]
    }

    uid = "wirehome.cc_tools.state_changed:" + wirehome.context["component_uid"]
    wirehome.message_bus.subscribe(uid, filter, __state_changed_callback__)

    __publish_state__()


def __publish_state__():
    service_parameters = {
        "device_uid": config["device_uid"],
        "port": config["port"]
    }

    service_result = wirehome.services.invoke(SERVICE_ID, "get_state", service_parameters)

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


def __state_changed_callback__(message):
    __publish_state__()
