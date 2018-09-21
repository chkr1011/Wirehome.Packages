SERVICE_ID = "wirehome.cc_tools.board_manager"


def process_adapter_message(properties):
    """
        Processes incoming messages from the ventilation component logic.

        Args:
            properties : {} = The properties of the message.
    """

    type = properties["type"]

    if type == "initialize":
        # TODO: Get the initial state from config. If not set use 0.
        init_result_type = __set__level__(0)["type"]

        global max_level
        level_definitions = config["level_definitions"]
        max_level = len(level_definitions) - 1

        return {
            "type": init_result_type,
            "level.max": max_level
        }
    elif type == "turn_off":
        return __set__level__(0)
    elif type == "set_level":
        level = properties.get("level", 0)

        if level > max_level or level < 0:
            return {"type": "exception.parameter_invalid"}

        return __set__level__(level)

    return {
        "type": "exception.not_supported"
    }


def __set__level__(index):
    try:
        level_definitions = config["level_definitions"]
        level_definition = level_definitions[index]

        for state in level_definition["states"]:
            parameters = {
                "device_uid": state["device_uid"],
                "port": state["port"],
                "state": state["state"],
                "commit": False
            }

            service_result = services.invoke(
                SERVICE_ID, "set_state", parameters)

            # TODO: Inspect service result.

        return services.invoke(SERVICE_ID, "commit_device_states")
    except:
        return {
            "type": "exception"
        }
