SERVICE_ID = "wirehome.services.cc_tools.board_manager"

config = {}


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()
    elif type == "turn_on":
        return __set_state_internal__("closed")
    elif type == "turn_off":
        return __set_state_internal__("open")
    elif type == "close":
        return __set_state_internal__("closed")
    elif type == "open":
        return __set_state_internal__("open")
    elif type == "set_state":
        return __set_state__(message)
    else:
        return wirehome.response_creator.not_supported(type)


def __initialize__():
    initial_state = config.get("initial_state", "open")
    return __set_state_internal__(initial_state)


def __set_state__(message):
    state = message.get("state", None)
    if state != None:
        if state == "on" or state == "closed" or state == "high":
            return __set_state_internal__("closed")
        else:
            return __set_state_internal__("open")

    power_state = message.get("power_state", None)
    if power_state != None:
        if power_state == "on":
            return __set_state_internal__("closed")
        else:
            return __set_state_internal__("open")

        return {
            "type": "exception.parameter_missing",
            "parameter_name": "power_state"
        }


def __set_state_internal__(state):
    try:
        for port in config.get("ports", []):
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

    return service_result
