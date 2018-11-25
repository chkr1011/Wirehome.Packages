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

        if new_state == "pressed":
            if component.get_setting("is_enabled", True) != False:
                component.set_status("button.state", "pressed")
        elif new_state == "released":
            component.set_status("button.state", "released")
        else:
            return {
                "type": "exception.not_supported",
                "new_state": new_state
            }

        return {
            "type": "success"
        }

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def __initialize__(message):
    component.set_status("button.state", "unknown")
    component.set_configuration("app.view_source", wirehome.package_manager.get_file_uri(scope["logic_uid"], "appView.html"))

    return publish_adapter_message({
        "type": "initialize"
    })
