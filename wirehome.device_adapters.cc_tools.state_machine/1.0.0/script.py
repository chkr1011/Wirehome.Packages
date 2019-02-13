SERVICE_ID = "wirehome.services.cc_tools.board_manager"

config = {}


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()
    elif type == "turn_on":
        return __set_state__("on")
    elif type == "turn_off":
        return __set_state__("off")
    elif type == "set_state":
        id = message["state"]
        return __set_state__(id)
    else:
        return {
            "type": "exception.not_supported",
            "origin_type": type
        }


def __initialize__():
    state_definitions = config.get("state_definitions", {})

    states = []
    for state in state_definitions.keys():
        states.append(state)

    initial_state = config.get("initial_state", None)

    if initial_state == None:
        initial_state = states[0]

    __set_state__(initial_state)

    return {
        "type": "success",
        "state": initial_state,
        "states": states
    }


def __set_state__(id):
    state_definitions = config.get("state_definitions", {})

    if id not in state_definitions:
        return {
            "type": "exception.not_supported",
            "state": id
        }

    state_definition = state_definitions[id]

    try:
        for state in state_definition:
            parameters = {
                "device_uid": state["device_uid"],
                "port": state["port"],
                "state": state["state"],
                "is_inverted": state.get("is_inverted", False),
                "commit": False
            }

            service_result = wirehome.services.invoke(SERVICE_ID, "set_state", parameters)
    finally:
        wirehome.services.invoke(SERVICE_ID, "commit_device_states")

    # TODO: Inspect service result!

    return {
        "type": "success"
    }
