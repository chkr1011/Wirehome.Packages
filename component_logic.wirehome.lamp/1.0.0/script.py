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
    type = message.get("type", None)
    if type == None:
        return

    if type == "power_state_changed":
        state = message.get("power_state", "off")

        if state == "on":
            component.set_status("power.state", "on")
        else:
            component.set_status("power.state", "off")


def __initialize__(message):
    component.set_status("power.state", "unknown")
    component.set_configuration("app.view_source", repository.get_file_uri(scope["logic_uid"], "appView.html"))

    adapter_result = publish_adapter_message({
        "type": "initialize"
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    if adapter_result.get("supports_brightness", False) == True:
        component.set_status("brightness.value", "unknown")

    return __set_state__("off")


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

    new_power_state = "off"

    if state == "on":
        new_power_state = "on"

        if static_power_consumption != None:
            component.set_status("power.consumption", static_power_consumption)

    elif state == "off":
        if static_power_consumption != None:
            component.set_status("power.consumption", 0)

    if adapter_result.get("skip_status_update", False) == False:
        component.set_status("power.state", new_power_state)

    return {
        "type": "success"
    }
