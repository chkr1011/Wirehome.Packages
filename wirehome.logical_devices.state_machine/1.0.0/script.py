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
    wirehome.component.set_status("state_machine.state", "unknown")
    wirehome.component.set_configuration("state_machine.states", "unknown")
    wirehome.component.set_configuration("app.view_source", wirehome.package_manager.get_file_uri(wirehome.context["logic_uid"], "appView.html"))

    adapter_result = wirehome.publish_adapter_message({
        "type": "initialize"
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    wirehome.component.set_configuration("state_machine.states", adapter_result["states"])
    wirehome.component.set_status("state_machine.state", adapter_result["state"])

    return {
        "type": "success"
    }


def __set_state__(state):
    adapter_result = wirehome.publish_adapter_message({
        "type": "set_state",
        "state": state
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    wirehome.component.set_status("state_machine.state", state)

    return {
        "type": "success"
    }
