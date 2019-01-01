config = {}


def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()
    if type == "enable":
        return __enable__()
    if type == "disable":
        return __disable__()
    else:
        return wirehome.response_creator.not_supported(type)


def __initialize__():
    __enable__()


def __enable__():
    global subscriptions
    subscriptions = []

    for button_uid in config["buttons"]:
        filter = {
            "type": "component_registry.event.status_changed",
            "component_uid": button_uid,
            "status_uid": "button.state",
            "new_value": "pressed"
        }

        subscription_uid = wirehome.context["component_uid"] + ":status_changed->" + button_uid
        wirehome.message_bus.subscribe(subscription_uid, filter, __button_callback__)
        subscriptions.append(subscription_uid)


def __disable__():
    global subscriptions

    for subscription_uid in subscriptions:
        wirehome.message_bus.unsubscribe(subscription_uid)

    subscriptions = []


def __button_callback__(message):
    for target_uid in config.get("targets", []):
        message = {"type": "toggle"}

        custom_states = config.get("custom_states", None)
        if custom_states != None:
            on_state = custom_states["on_state"]
            off_state = custom_states["off_state"]

            if not __status_is_match__(target_uid, on_state["status"]):
                message = on_state["message"]
            else:
                message = off_state["message"]

        wirehome.component_registry.process_message(target_uid, message)


def __status_is_match__(component_uid, status):
    for status_uid in status:
        current_status = wirehome.component_registry.get_status(component_uid, status_uid, None)
        expected_status = status[status_uid]

        if current_status != expected_status:
            return False

    return True
