# TODO: Add support for "last opened / tilt"
# TODO: Add support for "closed since".
# TODO: Add generic storage for storing that values.

import datetime

latest_state = None
component_uid = None

wirehome = {}

def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)

    return wirehome.response_creator.not_supported(type)


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "state_changed":
        new_state = message.get("new_state", None)

        global latest_state

        if (new_state == latest_state):
            return wirehome.response_creator.success()

        latest_state = new_state

        now = datetime.datetime.now().isoformat()

        if new_state == "open":
            wirehome.component.set_status("window.state", "open")
            wirehome.component.set_status("window.last_opened", now)
            #wirehome.value_storage.write("{c_uid}/last_opened".format(c_uid = component_uid), now)
        elif new_state == "closed":
            wirehome.component.set_status("window.state", "closed")
            wirehome.component.set_status("window.last_closed", now)
            #wirehome.value_storage.write("{c_uid}/last_closed".format(c_uid = component_uid), now)
        elif new_state == "tilt":
            wirehome.component.set_status("window.state", "tilt")
            wirehome.component.set_status("window.last_tilt", now)
            #wirehome.value_storage.write("{c_uid}/last_tilt".format(c_uid = component_uid), now)

        return wirehome.response_creator.success()

    return wirehome.response_creator.not_supported(type)


def __initialize__(message):
    global component_uid
    component_uid = wirehome.context["component_uid"]

    wirehome.component.set_status("window.state", "unknown")

    #wirehome.component.set_status("window.last_opened", wirehome.value_storage.read(
    #    "{c_uid}/last_opened".format(c_uid = component_uid), None))

    #wirehome.component.set_status("window.last_closed", wirehome.value_storage.read(
    #    "{c_uid}/last_closed".format(c_uid = component_uid), None))

    #wirehome.component.set_status("window.last_tilt", wirehome.value_storage.read(
    #    "{c_uid}/last_tilt".format(c_uid = component_uid), None))

    #wirehome.component.set_configuration("app.view_source", wirehome.package_manager.get_file_uri(
    #    wirehome.context["logic_uid"], "appView.html"))

    return wirehome.publish_adapter_message({
        "type": "initialize"
    })
