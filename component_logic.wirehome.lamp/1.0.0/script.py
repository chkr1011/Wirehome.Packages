_power_state = "off"
_brightness = 100
_color = "ffffff"
_supports_brightness = False


def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)
    elif type == "turn_off":
        return __turn_off__()
    elif type == "turn_on":
        return __turn_on__()
    elif type == "toggle":
        return __toggle__()
    elif type == "set_brightness":
        return __set_brightness__(message)
    elif type == "increase_brightness":
        return __increase_brightness__(message)
    elif type == "decrease_brightness":
        return __decrease_brightness__(message)
    else:
        return {
            "type": "exception.not_supported",
            "origin_type": type
        }


def __turn_on__():
    global _power_state
    _power_state = "on"
    return __set_state__()


def __turn_off__():
    global _power_state
    _power_state = "off"
    return __set_state__()


def __toggle__():
    global _power_state
    if _power_state == "off":
        return __turn_on__()
    else:
        return __turn_off__()


def __set_brightness__(message):
    global _brightness
    _brightness = message.get("brightness", 0)
    return __set_state__()


def __increase_brightness__(message):
    global _brightness
    _brightness += message.get("value", 5)
    return __set_state__()


def __decrease_brightness__(message):
    global _brightness
    _brightness -= message.get("value", 5)
    return __set_state__()


def process_adapter_message(message):
    """
    This is the backward channel which receives the state update from the device.
    """

    global _power_state

    type = message.get("type", None)
    if type == None:
        return

    if type == "power_state_changed":
        state = message.get("power_state", "off")

        if state == "on":
            _power_state = "on"
        else:
            _power_state = "off"

    wirehome.component.set_status("power.state", _power_state)


def __initialize__(message):
    wirehome.component.set_status("power.state", "unknown")
    wirehome.component.set_configuration("app.view_source", wirehome.repository.get_file_uri(context["logic_uid"], "appView.html"))

    adapter_result = publish_adapter_message({
        "type": "initialize"
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    global _supports_brightness
    _supports_brightness = adapter_result.get("supports_brightness", False)

    if _supports_brightness:
        wirehome.component.set_status("brightness.value", "unknown")

    return __set_state__()


def __set_state__():
    message = {
        "type": "set_state",
        "power_state": _power_state
    }

    if _supports_brightness:
        global _brightness
        if _brightness > 100:
            _brightness = 100
        elif _brightness < 0:
            _brightness = 0

        message["brightness"] = _brightness

    adapter_result = publish_adapter_message(message)

    if adapter_result.get("type", None) != "success" and adapter_result.get("type", None) != "exception.not_supported":
        return adapter_result

    skip_status_update = adapter_result.get("skip_status_update", False)

    static_power_consumption = globals().get("config", {}).get("static_power_consumption", None)

    if _power_state == "on":
        publish_adapter_message({"type": "turn_on"})  # Only for backward compatibility.

        if static_power_consumption != None:
            wirehome.component.set_status("power.consumption", static_power_consumption)
    elif _power_state == "off":
        publish_adapter_message({"type": "turn_off"})  # Only for backward compatibility.

        if static_power_consumption != None:
            wirehome.component.set_status("power.consumption", 0)

    if not skip_status_update:
        wirehome.component.set_status("power.state", _power_state)

        if _supports_brightness:
            wirehome.component.set_status("brightness.value", _brightness)

    if adapter_result.get("type", None) != "success":
        return adapter_result

    return wirehome.response_creator.success()
