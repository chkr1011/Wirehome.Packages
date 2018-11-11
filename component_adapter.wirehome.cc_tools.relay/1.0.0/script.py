SERVICE_ID = "service.wirehome.cc_tools.board_manager"


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()
    elif type == "turn_on":
        return __turn_on__()
    elif type == "turn_off":
        return __turn_off__()
    elif type == "set_state":
        return __set_state__(message)
    else:
        return {
            "type": "exception.not_supported",
            "origin_type": type
        }


def __initialize__():
    return __turn_off__()


def __set_state__(message):
    power_state = message.get("power_state", None)
    if power_state == None:
        return {
            "type": "exception.parameter_missing",
            "parameter_name": "power_state"
        }

    if power_state == "on":
        return __turn_on__()
    else:
        return __turn_off__()


def __turn_on__():
    return __set_state_internal__("closed")


def __turn_off__():
    return __set_state_internal__("open")


def __set_state_internal__(state):
    # TODO: Use function pool "wirehome.cc_tools.board_manager.set_state"

    try:
        for port in config.get("ports", {}):
            parameters = {
                "device_uid": port["device_uid"],
                "port": port["port"],
                "is_inverted": port.get("is_inverted", False),
                "state": state,
                "commit": False
            }

            service_result = wirehome.services.invoke(SERVICE_ID, "set_state", parameters)
    finally:
        wirehome.services.invoke(SERVICE_ID, "commit_device_states")

    # TODO: Inspect service result!

    return wirehome.response_creator.success()
