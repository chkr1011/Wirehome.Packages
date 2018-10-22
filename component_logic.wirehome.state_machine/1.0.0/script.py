def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)
    elif type == "turn_off":
        return __set_state__("off")
    elif type == "turn_on":
        return __set_state__("on")
    elif type == "set_state":
        state = message.get("state", None)
        return __set_state__(state)

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def process_adapter_message(message):
    pass


def __initialize__(message):
    component.set_status("state_machine.state", "unknown")
    component.set_configuration("state_machine.states", "unknown")
    component.set_configuration("app.view_source", repository.get_file_uri(scope["logic_uid"], "appView.html"))

    adapter_result = publish_adapter_message({
        "type": "initialize"
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    component.set_configuration("state_machine.states", adapter_result["states"])
    component.set_status("state_machine.state", adapter_result["state"])

    return {
        "type": "success"
    }


def __set_state__(state):

    adapter_result = publish_adapter_message({
        "type": "set_state",
        "state": state
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    component.set_status("state_machine.state", state)

    return {
        "type": "success"
    }
