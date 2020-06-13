_power_state = "off"
_brightness = 100
_color = "#FFFFFF"
_supports_brightness = False
_supports_color = False

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
    elif type == "set_color":
        return __set_color__(message)
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


def __set_color__(message):
    global _color
    _color = message.get("color", "#FFFFFF")
    return __set_state__()


def process_adapter_message(message):
    """
    This is the backward channel which receives the state update from the device.
    """

    global _power_state, _brightness, _color

    type = message.get("type", None)
    if type == None:
        return

    if type == "power_state_changed":
        _power_state = message.get("power_state", _power_state)
        wirehome.component.set_status("power.state", _power_state)

        if _supports_brightness:
            _brightness = message.get("brightness", _brightness)
            wirehome.component.set_status("brightness.value", _brightness)

        if _supports_color:
            _color = message.get("color", _color)
            wirehome.component.set_status("color.value", _color)


def __initialize__(message):
    wirehome.component.set_status("power.state", "unknown")
    wirehome.component.set_configuration("app.view_source", wirehome.package_manager.get_file_uri(wirehome.context["logic_uid"], "appView.html"))

    adapter_result = wirehome.publish_adapter_message({
        "type": "initialize"
    })

    if adapter_result.get("type", None) != "success":
        wirehome.log.warning("Initialization of lamp '{componentUid}' failed (Adapter result = {result}).".format(
            componentUid=wirehome.context["component_uid"], result=str(adapter_result)))
        return adapter_result

    global _supports_brightness, _supports_color
    _supports_brightness = adapter_result.get("supports_brightness", False)
    _supports_color = adapter_result.get("supports_color", False)

    if _supports_brightness:
        wirehome.component.set_status("brightness.value", "unknown")

    if _supports_color:
        wirehome.component.set_status("color.value", "unknown")

        colors = [{"value": "#FF0000"},
                  {"value": "#00FF00"},
                  {"value": "#0000FF"},
                  {"value": "#FFFF00"},
                  {"value": "#800080"},
                  {"value": "#FFFFFF"}]

        wirehome.component.set_configuration("colors", colors)

    return __set_state__()


def __set_state__():
    is_enabled = wirehome.component.get_setting("is_enabled", True)
    if not is_enabled:
        return wirehome.response_creator.disabled()

    adapter_message = {
        "type": "set_state",
        "power_state": _power_state
    }

    if _supports_brightness:
        global _brightness
        if _brightness > 100:
            _brightness = 100
        elif _brightness < 0:
            _brightness = 0

        adapter_message["brightness"] = _brightness

    if _supports_color:
        adapter_message["color"] = _color

    adapter_result = wirehome.publish_adapter_message(adapter_message)

    if adapter_result.get("type", None) != "success" and adapter_result.get("type", None) != "exception.not_supported":
        return adapter_result

    skip_status_update = adapter_result.get("skip_status_update", False)

    static_power_consumption = config.get("static_power_consumption", None)

    power_consumption = 0

    if _power_state == "on" and static_power_consumption != None:
        power_consumption = static_power_consumption

    wirehome.component.set_status("power.consumption", power_consumption)

    if not skip_status_update:
        wirehome.component.set_status("power.state", _power_state)

        if _supports_brightness:
            wirehome.component.set_status("brightness.value", _brightness)

    if adapter_result.get("type", None) != "success":
        return adapter_result

    return wirehome.response_creator.success()


def __disable__():
    wirehome.component.set_setting("is_enabled", False)
    return wirehome.response_creator.success()


def __enable__():
    wirehome.component.set_setting("is_enabled", True)
    return wirehome.response_creator.success()
