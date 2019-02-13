config = {}


def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)
    elif type == "open":
        return __set_state__("open")
    elif type == "close":
        return __set_state__("closed")
    elif type == "set_state":
        return __set_state__(message["state"])
    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def process_adapter_message(message):
    pass


def __initialize__(message):
    wirehome.component.set_status("valve.state", "unknown")
    wirehome.component.set_configuration("app.view_source", wirehome.package_manager.get_file_uri(wirehome.context["logic_uid"], "appView.html"))

    adapter_result = wirehome.publish_adapter_message({
        "type": "initialize"
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    initial_state = config.get("initial_state", "open")
    return __set_state__(initial_state)


def __set_state__(state):
    message = {
        "type": "set_state",
        "state": state
    }

    adapter_result = wirehome.publish_adapter_message(message)

    if adapter_result.get("type", None) != "success":
        return adapter_result

    static_power_consumption = config.get("static_power_consumption", None)

    if state == "open":
        wirehome.component.set_status("valve.state", "open")

        if static_power_consumption != None:
            wirehome.component.set_status("power.consumption", 0)

    elif state == "closed":
        wirehome.component.set_status("valve.state", "closed")

        if static_power_consumption != None:
            wirehome.component.set_status("power.consumption", static_power_consumption)

    return {
        "type": "success"
    }
