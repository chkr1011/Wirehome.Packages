def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)
    elif type == "turn_off":
        return __set_level__(0)
    elif type == "set_level":
        level = message.get("level", 0)
        return __set_level__(level)
    elif type == "increase_level":
        current_level = component.get_status("level.current")
        current_level += 1

        max_level = component.get_configuration("level.max")
        if current_level > max_level:
            current_level = 0

        return __set_level__(current_level)
    elif type == "decrease_level":
        current_level = component.get_status("level.current")
        current_level -= 1

        if current_level < 0:
            current_level = component.get_configuration("level.max")

        return __set_level__(current_level)

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def process_adapter_message(message):
    pass


def __initialize__(message):
    component.set_status("level.current", "unknown")
    component.set_configuration("level.max", "unknown")
    component.set_configuration("app.view_source", repository.get_file_uri(scope["logic_uid"], "appView.html"))

    adapter_result = publish_adapter_message({
        "type": "initialize"
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    max_level = adapter_result.get("level.max", 0)  # Use max_level
    component.set_configuration("level.max", max_level)
    return __set_level__(0)


def __set_level__(level):
    adapter_result = publish_adapter_message({
        "type": "set_level",
        "level": level
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    component.set_status("level.current", level)

    return {
        "type": "success"
    }
