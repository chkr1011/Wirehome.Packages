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
        if new_state == "pressed":
            component.set_status("button.state", "pressed")
        elif new_state == "released":
            component.set_status("button.state", "released")

        return {
            "type": "success"
        }

    return {
        "type": "not_supported"
    }


def __initialize__(message):
    component.set_status("button.state", "released")
    publish_adapter_message({
        "type": "initialize"
    })

    return {
        "type": "success"
    }
