# TODO: Add support for "last opened / tilt"
# TODO: Add support for "closed since".
# TODO: Add generic storage for storing that values.

import datetime


def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)

    return wirehome.response_creator.not_supported(type)


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "state_changed":
        new_state = message.get("new_state", None)

        now = datetime.datetime.now().isoformat()

        if new_state == "open":
            wirehome.component.set_status("window.state", "open")
            wirehome.component.set_status("window.last_opened", now)
            wirehome.value_storage.write(wirehome.context["component_uid"], "last_opened", now)
        elif new_state == "closed":
            wirehome.component.set_status("window.state", "closed")
            wirehome.component.set_status("window.last_closed", now)
            wirehome.value_storage.write(wirehome.context["component_uid"], "last_closed", now)
        elif new_state == "tilt":
            wirehome.component.set_status("window.state", "tilt")
            wirehome.component.set_status("window.last_tilt", now)
            wirehome.value_storage.write(wirehome.context["component_uid"], "last_tilt", now)

        return wirehome.response_creator.success()

    return wirehome.response_creator.not_supported(type)


def __initialize__(message):
    wirehome.component.set_status("window.state", "unknown")
    wirehome.component.set_status("window.last_opened", wirehome.value_storage.read(wirehome.context["component_uid"], "last_opened", None))

    wirehome.component.set_configuration("app.view_source", wirehome.package_manager.get_file_uri(wirehome.context["logic_uid"], "appView.html"))

    return wirehome.publish_adapter_message({
        "type": "initialize"
    })
