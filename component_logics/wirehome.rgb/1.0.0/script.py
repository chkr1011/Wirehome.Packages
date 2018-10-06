def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()
    elif type == "turn_off":
        return __turn_off__()
    elif type == "turn_on":
        return __turn_on__()
    elif type == "toggle":
        return __toggle__()
    elif type == "set_color":
        return __set_color__(message)

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def process_adapter_message(message):
    pass


def __initialize__():
    config_default_color = config.get("default_color", {})

    global default_color
    default_color = {
        "r": config_default_color.get("red", 255),
        "g": config_default_color.get("green", 255),
        "b": config_default_color.get("blue", 255)
    }

    global last_color
    last_color = {
        "r": default_color.get("r", 255),
        "g": default_color.get("g", 255),
        "b": default_color.get("b", 255)
    }

    component.set_status("power.state", "unknown")
    component.set_status("color.red", "unknown")
    component.set_status("color.green", "unknown")
    component.set_status("color.blue", "unknown")

    adapter_result = publish_adapter_message({
        "type": "initialize"
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    return __turn_off__()


def __turn_off__():
    adapter_result = publish_adapter_message({
        "type": "turn_off"
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    component.set_status("power.state", "off")
    component.set_status("color.red", 0)
    component.set_status("color.green", 0)
    component.set_status("color.blue", 0)

    return {"type": "success"}


def __turn_on__():
    r = last_color["r"]
    g = last_color["g"]
    b = last_color["b"]

    is_off = r == 0 and g == 0 and b == 0
    if is_off:
        r = default_color["r"]
        g = default_color["g"]
        b = default_color["b"]

    return __apply_color__(r, g, b)


def __toggle__():
    is_off = component.get_status("power.state", "off") == "off"
    if is_off:
        return __turn_on__()
    else:
        return __turn_off__()


def __set_color__(message):
    format = message.get("format", "rgb")

    r = 0
    g = 0
    b = 0

    if format == "rgb":
        r = message.get("r", 0)
        g = message.get("g", 0)
        b = message.get("b", 0)
    elif format == "hsv":
        pass
    elif format == "hex":
        pass
    else:
        return {
            "type": "exception.not_supported",
            "parameter_name": "format",
            "parameter_value": format
        }

    return __apply_color__(r, g, b)


def __apply_color__(r, g, b):
    parameters = {
        "type": "set_color",
        "format": "rgb",
        "r": r,
        "g": g,
        "b": b
    }

    adapter_result = publish_adapter_message(parameters)

    if adapter_result.get("type", None) != "success":
        return adapter_result

    component.set_status("color.red", r)
    component.set_status("color.green", g)
    component.set_status("color.blue", b)

    is_off = r == 0 and g == 0 and b == 0
    if is_off:
        component.set_status("power.state", "off")
    else:
        component.set_status("power.state", "on")

    global last_color
    last_color["r"] = r
    last_color["g"] = g
    last_color["b"] = b

    return {"type": "success"}
