config = {}


def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)
    elif type == "disable":
        return __disable__()
    elif type == "enable":
        return __enable__()
    elif type == "turn_off":
        return __set_state__("off")
    elif type == "turn_on":
        return __set_state__("on")
    elif type == "toggle":
        if wirehome.component.get_status("power.state") == "off":
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

    wirehome.component.set_status("power.state", "unknown")
    wirehome.component.set_configuration("app.view_source", wirehome.package_manager.get_file_uri(wirehome.context["logic_uid"], "appView.html"))

    adapter_result = wirehome.publish_adapter_message({
        "type": "initialize"
    })

    if adapter_result.get("type", None) != "success":
        wirehome.log.warning("Initialization of socket '{componentUid}' failed (Adapter result = {result}).".format(componentUid = wirehome.context["component_uid"], result = str(adapter_result)))
        return adapter_result

    initial_state = config.get("initial_state", "off")
    return __set_state__(initial_state)


def __set_state__(state):
    is_enabled = wirehome.component.get_setting("is_enabled", True)
    if not is_enabled:
        return wirehome.response_creator.disabled()

    if state == "on":
        type = "turn_on"
    elif state == "off":
        type = "turn_off"

    adapter_result = wirehome.publish_adapter_message({
        "type": type
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    static_power_consumption = config.get("static_power_consumption", None)

    if state == "on":
        wirehome.component.set_status("power.state", "on")

        if static_power_consumption != None:
            wirehome.component.set_status("power.consumption", static_power_consumption)

    elif state == "off":
        wirehome.component.set_status("power.state", "off")

        if static_power_consumption != None:
            wirehome.component.set_status("power.consumption", 0)

    return {
        "type": "success"
    }

def __disable__():
    wirehome.component.set_setting("is_enabled", False)
    return wirehome.response_creator.success()


def __enable__():
    wirehome.component.set_setting("is_enabled", True)
    return wirehome.response_creator.success()