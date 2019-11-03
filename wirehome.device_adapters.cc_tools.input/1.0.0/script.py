SERVICE_ID = "wirehome.services.cc_tools.board_manager"

config = {}


def process_adapter_message(message):
    type = message.get("type", None)
    if type == "initialize":
        return __initialize__()
    else:
        return wirehome.response_creator.not_supported(type)


def __initialize__():
    filter = {
        "type": "cc_tools.board_manager.event.state_changed",
        "device_uid": config["device_uid"]
    }

    uid = "wirehome.cc_tools.state_changed:" + wirehome.context["component_uid"]
    wirehome.message_bus.subscribe(uid, filter, __state_changed_callback__)

    __publish_state__()

    return wirehome.response_creator.success()


def __publish_state__():
    get_state_parameters = {
        "device_uid": config["device_uid"],
        "port":  config["port"]
    }

    # Get the effective pin state because the event from the CCTools board manager
    # only contains the overall state of the device.
    service_result = wirehome.services.invoke(SERVICE_ID, "get_state", get_state_parameters)
    pin_state = service_result["pin_state"]

    # Most of the CCTools devices have pull ups and are connected to GND
    # in case a switch is closing etc.
    is_inverted = config.get("is_inverted", True)

    if is_inverted == True and pin_state == "low":
        pin_state = "high"
    elif is_inverted == True and pin_state == "high":
        pin_state = "low"

    message = {
        "type": "state_changed",
        "new_state": pin_state
    }

    wirehome.publish_adapter_message(message)


def __state_changed_callback__(properties):
    __publish_state__()
