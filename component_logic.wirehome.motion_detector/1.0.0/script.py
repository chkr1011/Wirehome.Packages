def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)
    if type == "destroy":
        return __destroy__(message)
    else:
        return {
            "type": "exception.not_supported",
            "origin_type": type
        }


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "state_changed":
        new_state = message.get("new_state", None)

        if new_state == "idle":
            wirehome.component.set_status("motion_detection.state", "idle")
        elif new_state == "detected":
            is_enabled = wirehome.component.get_setting("is_enabled", True)
            if is_enabled:
                wirehome.component.set_status("motion_detection.state", "detected")

        return {
            "type": "success"
        }

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def __initialize__(message):
    wirehome.component.set_status("motion_detection.state", "unknown")

    app_view_uri = wirehome.repository.get_file_uri(context["logic_uid"], "appView.html")

    wirehome.component.set_configuration("app.view_source", app_view_uri)

    return publish_adapter_message({
        "type": "initialize"
    })


def __destroy__(message):
    return publish_adapter_message({
        "type": "destroy"
    })
