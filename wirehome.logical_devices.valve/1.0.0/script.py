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
        return __set_state__(message.get("state", None))
    else:
        return wirehome.response_creator.not_supported(type)


def process_adapter_message(message):
    pass


def __initialize__(message):
    wirehome.component.set_status("valve.state", "unknown")
    wirehome.component.set_configuration("app.view_source", wirehome.package_manager.get_file_uri(wirehome.context["logic_uid"], "appView.html"))

    adapter_result = wirehome.publish_adapter_message({
        "type": "initialize"
    })

    if adapter_result.get("type", None) != "success":
        wirehome.log.warning("Initialization of valve '{componentUid}' failed (Adapter result = {result}).".format(componentUid = wirehome.context["component_uid"], result = str(adapter_result)))
        return adapter_result

    initial_state = config.get("initial_state", "closed")
    return __set_state__(initial_state)


def __set_state__(state):
    valve_is_inverted = config.get("is_inverted", True),  # The most valves for heating are open of power is lost.

    effective_state = state

    if valve_is_inverted:
        if effective_state == "open":
            effective_state = "closed"
        else:
            effective_state = "open"

    message = {
        "type": "set_state",
        "state": effective_state
    }

    adapter_result = wirehome.publish_adapter_message(message)

    if adapter_result.get("type", None) != "success":
        return adapter_result

    static_power_consumption = config.get("static_power_consumption", {})

    if state == "open":
        wirehome.component.set_status("valve.state", "open")
        wirehome.component.set_status("power.consumption", static_power_consumption.get("open", 0))

    elif state == "closed":
        wirehome.component.set_status("valve.state", "closed")
        wirehome.component.set_status("power.consumption", static_power_consumption.get("closed", 0))

    return {
        "type": "success"
    }
