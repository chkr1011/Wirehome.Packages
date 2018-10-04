def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)
    elif type == "turn_off":
        return __set_state__("turn_off")
    elif type == "move_up":
        return __set_state__("move_up")
    elif type == "move_down":
        return __set_state__("move_down")

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def process_adapter_message(message):
    pass


def __initialize__(message):
    component.set_status("roller_shutter.state", "unknown")
    component.set_status("roller_shutter.position", "unknown")
    component.set_status("power.state", "unknown")
    component.set_status("power.consumption", "unknown")

    adapter_result = publish_adapter_message({
        "type": "initialize"
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    return __set_state__("turn_off")


def __set_state__(state):
    adapter_result = publish_adapter_message({
        "type": state
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    # The power consumption from the adapter has a higher precedence (if supported and delivered)!
    power_consumption = adapter_result.get("power.consumption", None)

    if power_consumption == None:
        power_consumption = globals().get("config", {}).get("static_power_consumption", None)

    if state == "turn_off":
        component.set_status("roller_shutter.state", "off")
        component.set_status("roller_shutter.position", 0)
        component.set_status("power.state", "off")

        if power_consumption != None:
            component.set_status("power.consumption", 0)

    if state == "move_up":
        component.set_status("roller_shutter.state", "moving_up")
        component.set_status("power.state", "on")

        if power_consumption != None:
            component.set_status("power.consumption", power_consumption)

        start_auto_off_countdown = True

    if state == "move_down":
        component.set_status("roller_shutter.state", "moving_down")
        component.set_status("power.state", "on")

        if power_consumption != None:
            component.set_status("power.consumption", power_consumption)

        start_auto_off_countdown = True

    auto_off_timeout = globals().get("config", {}).get("auto_off_timeout", 60000)
    start_auto_off_countdown = state == "move_up" or state == "move_down"

    if start_auto_off_countdown == True and auto_off_timeout != None:
        countdown_uid = scope["component_uid"] + ".auto_off"
        scheduler.start_countdown(countdown_uid, auto_off_timeout, __auto_off_callback__)

    return {
        "type": "success"
    }


def __auto_off_callback__(_):
    __set_state__("turn_off")
