SERVICE_ID = "wirehome.services.cc_tools.board_manager"

config = {}


def process_adapter_message(message):
    type = message.get("type", None)
    if type == "initialize":
        return __initialize__()
    else:
        return wirehome.response_creator.not_supported(type)


def __initialize__():
    open_port_config = config.get("open_port")
    filter = {
        "type": "cc_tools.board_manager.event.state_changed",
        "device_uid": open_port_config["device_uid"]
    }

    uid = "wirehome.cc_tools.state_changed/open:" + wirehome.context["component_uid"]
    wirehome.message_bus.subscribe(uid, filter, __state_changed_callback__)

    tilt_port_config = config.get("tilt_port", None)  # Optional
    if tilt_port_config != None:
        filter = {
            "type": "cc_tools.board_manager.event.state_changed",
            "device_uid": tilt_port_config["device_uid"]
        }

        uid = "wirehome.cc_tools.state_changed/tilt:" + wirehome.context["component_uid"]
        wirehome.message_bus.subscribe(uid, filter, __state_changed_callback__)

    __publish_state__()

    return wirehome.response_creator.success()


def __publish_state__():
    # Get the effective pin state because the event from the CCTools board manager
    # only contains the overall state of the device.
    tilt_port_config = config.get("tilt_port", None)  # Optional
    if tilt_port_config != None:
        get_state_result = wirehome.services.invoke(SERVICE_ID, "get_state", {"device_uid": tilt_port_config["device_uid"], "port": tilt_port_config["port"]})
        tilt_port_state = get_state_result["pin_state"]

        if (tilt_port_state == tilt_port_config.get("expected_pin_state", "high")):
            wirehome.publish_adapter_message({"type": "state_changed", "new_state": "tilt"})
            return

    open_port_config = config.get("open_port")
    get_state_result = wirehome.services.invoke(SERVICE_ID, "get_state", {"device_uid": open_port_config["device_uid"], "port": open_port_config["port"]})
    open_pin_state = get_state_result["pin_state"]

    if (open_pin_state == open_port_config.get("expected_pin_state", "high")):
        wirehome.publish_adapter_message({"type": "state_changed", "new_state": "open"})
        return

    wirehome.publish_adapter_message({"type": "state_changed", "new_state": "closed"})


def __state_changed_callback__(properties):
    __publish_state__()
