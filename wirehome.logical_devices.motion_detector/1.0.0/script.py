import datetime

config = {}


def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)
    if type == "destroy":
        return __destroy__(message)
    if type == "enable":
        return __enable__()
    if type == "disable":
        return __disable__(message)
    else:
        return wirehome.response_creator.not_supported(type)


def process_adapter_message(message):
    type = message.get("type", None)

    if type != "state_changed":
        return wirehome.response_creator.not_supported(type)

    new_state = message.get("new_state", None)

    update_last_detection = False

    if new_state == "idle":
        wirehome.component.set_status("motion_detection.state", "idle")
        update_last_detection = True
    elif new_state == "detected":
        is_enabled = wirehome.component.get_setting("is_enabled", True)
        if is_enabled:
            wirehome.component.set_status("motion_detection.state", "detected")
            update_last_detection = True

    if update_last_detection:
        # Also change on _idle_ because detection may have a duration of several minutes.
        wirehome.component.set_status("motion_detection.last_detection", datetime.datetime.now().isoformat())

    return wirehome.response_creator.success()


def __initialize__(message):
    global auto_activate_countdown_uid
    auto_activate_countdown_uid = wirehome.context["component_uid"] + ".auto_activate.countdown"

    wirehome.component.set_status("motion_detection.state", "unknown")

    app_view_uri = wirehome.package_manager.get_file_uri(wirehome.context["logic_uid"], "appView.html")

    wirehome.component.set_configuration("app.view_source", app_view_uri)

    return wirehome.publish_adapter_message({
        "type": "initialize"
    })


def __destroy__(message):
    return wirehome.publish_adapter_message({
        "type": "destroy"
    })


def __disable__(message):
    wirehome.component.set_setting("is_enabled", False)

    if wirehome.component.get_setting("auto_activate.is_enabled", False):
        delay = wirehome.component.get_setting("auto_activate.delay", 5 * 60)  # Default to 5 minutes.

        wirehome.scheduler.start_countdown(auto_activate_countdown_uid, delay * 1000, __auto_activate_callback__)

    return wirehome.response_creator.success()


def __enable__():
    wirehome.scheduler.stop_countdown(auto_activate_countdown_uid)

    wirehome.component.set_setting("is_enabled", True)

    return wirehome.response_creator.success()


def __auto_activate_callback__(_):
    return __enable__()
