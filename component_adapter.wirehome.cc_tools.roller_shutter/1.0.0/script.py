SERVICE_ID = "service.wirehome.cc_tools.board_manager"


def process_adapter_message(properties):
    """
        Processes incoming messages from the ventilation component logic.

        Args:
            properties : {} = The properties of the message.
    """

    type = properties["type"]

    if type == "initialize":
        return __set__state__("off")
    elif type == "turn_off":
        return __set__state__("off")
    elif type == "move_up":
        return __set__state__("moving_up")
    elif type == "move_down":
        return __set__state__("moving_down")

    return {
        "type": "exception.not_supported"
    }


def __set__state__(uid):
    # TODO: Use function pool

    try:
        states = config["state_definitions"][uid]

        for state in states:
            parameters = {
                "device_uid": state["device_uid"],
                "port": state["port"],
                "state": state["state"],
                "commit": False
            }

            service_result = services.invoke(SERVICE_ID, "set_state", parameters)

            # TODO: Inspect service result.

        return services.invoke(SERVICE_ID, "commit_device_states")
    except Exception as ex:
        print(ex)
        return {
            "type": "exception",
            "details": ""
        }
