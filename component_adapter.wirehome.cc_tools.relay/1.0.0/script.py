SERVICE_ID = "service.wirehome.cc_tools.board_manager"


def process_adapter_message(properties):
    """
        Processes incoming messages from the component logic.

        Args:
            properties : {} = The properties of the message.
    """

    type = properties.get("type", "")

    if type == "initialize":
        return __initialize__()
    elif type == "turn_on":
        return __turn_on__()
    elif type == "turn_off":
        return __turn_off__()

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def __initialize__():
    return __turn_off__()


def __turn_on__():
    return __set_state__("closed")


def __turn_off__():
    return __set_state__("open")


def __set_state__(state):
    # TODO: Use function pool "wirehome.cc_tools.board_manager.set_state"

    try:
        for port in config["ports"]:
            parameters = {
                "device_uid": port["device_uid"],
                "port": port["port"],
                "is_inverted": port.get("is_inverted", False),
                "state": state,
                "commit": False
            }

            service_result = services.invoke(SERVICE_ID, "set_state", parameters)

    finally:
        services.invoke(SERVICE_ID, "commit_device_states")

    # TODO: Use function pool "wirehome.cc_tools.board_manager.commit_device_states"

    # TODO: Inspect service result!

    result = {
        "type": "success"
    }

    return result
