def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "state_changed":
        new_state = message.get("new_state", None)

        if new_state == "open":
            component.set_status("window.state", "open")
        elif new_state == "closed":
            component.set_status("window.state", "closed")
        elif new_state == "tilt":
            component.set_status("window.state", "detected")

        return {
            "type": "success"
        }

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def __initialize__(message):
    component.set_status("window.state", "unknown")
    component.set_configuration("app.view_source", wirehome.package_manager.get_file_uri(scope["logic_uid"], "appView.html"))

    return publish_adapter_message({
        "type": "initialize"
    })
