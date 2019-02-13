config = {}


def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)
    if type == "enable":
        return __enable__()
    if type == "disable":
        return __disable__()
    else:
        return wirehome.response_creator.not_supported(type)


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "state_changed":
        return __on_state_changed__(message)

    return wirehome.response_creator.not_supported(type)


def __on_state_changed__(message):
    new_state = message.get("new_state", None)
    countdown_uid = "wirehome.button->triggered_long_event_countdown->" + wirehome.context["component_uid"]
    long_press_max_duration = config.get("long_press_max_duration", 2500)

    if new_state == "pressed":
        if wirehome.component.get_setting("is_enabled", True) != False:
            wirehome.component.set_status("button.state", "pressed")
            wirehome.scheduler.start_countdown(countdown_uid, long_press_max_duration, __send_triggered_long_event__)
    elif new_state == "released":
        wirehome.component.set_status("button.state", "released")

        if wirehome.scheduler.stop_countdown(countdown_uid):
            __send_triggered_short_event__(None)
    else:
        return {
            "type": "exception.not_supported",
            "new_state": new_state
        }

    return {
        "type": "success"
    }


def __send_triggered_long_event__(_):
    wirehome.message_bus.publish({
        "type": "wirehome.button.event.triggered",
        "component_uid": wirehome.context["component_uid"],
        "duration": "long"
    })


def __send_triggered_short_event__(_):
    wirehome.message_bus.publish({
        "type": "wirehome.button.event.triggered",
        "component_uid": wirehome.context["component_uid"],
        "duration": "short"
    })


def __initialize__(message):
    wirehome.component.set_status("button.state", "unknown")
    wirehome.component.set_configuration("app.view_source", wirehome.package_manager.get_file_uri(wirehome.context["logic_uid"], "appView.html"))

    return wirehome.publish_adapter_message({
        "type": "initialize"
    })


def __disable__():
    wirehome.component.set_setting("is_enabled", False)

    return {
        "type": "success"
    }


def __enable__():
    wirehome.component.set_setting("is_enabled", True)

    return {
        "type": "success"
    }
