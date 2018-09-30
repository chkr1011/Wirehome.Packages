def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)

    return {
        "type": "exception.not_supported"
    }


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "state_changed":
        new_state = message.get("new_state", None)

        if new_state == "idle":
            component.set_status("motion_detection.state", "idle")
        elif new_state == "detected":
            component.set_status("motion_detection.state", "detected")

        return {
            "type": "success"
        }

    return {
        "type": "not_supported"
    }


def __initialize__(message):
    component.set_status("motion_detection.state", "unknown")
    publish_adapter_message({
        "type": "initialize"
    })

    return {
        "type": "success"
    }
