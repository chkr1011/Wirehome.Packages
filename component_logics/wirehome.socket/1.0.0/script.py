def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)
    elif type == "turn_off":
        return __set_state__("off")
    elif type == "turn_on":
        return __set_state__("on")
    elif type == "toggle":
        if component.get_status("power.state") == "off":
            return __set_state__("on")
        else:
            return __set_state__("off")

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def process_adapter_message(message):
    pass


def __initialize__(message):
    # Use a static value for power consumption here if added to the config.

    component.set_status("power.state", "unknown")
    adapter_result = publish_adapter_message({
        "type": "initialize"
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    initial_state = globals().get("config", {}).get("initial_state", "off")

    return __set_state__(initial_state)


def __set_state__(state):

    if state == "on":
        type = "turn_on"
    elif state == "off":
        type = "turn_off"

    adapter_result = publish_adapter_message({
        "type": type
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    static_power_consumption = globals().get("config", {}).get("static_power_consumption", None)

    if state == "on":
        component.set_status("power.state", "on")

        if static_power_consumption != None:
            component.set_status("power.consumption", static_power_consumption)

    elif state == "off":
        component.set_status("power.state", "off")

        if static_power_consumption != None:
            component.set_status("power.consumption", 0)

    return {
        "type": "success"
    }
