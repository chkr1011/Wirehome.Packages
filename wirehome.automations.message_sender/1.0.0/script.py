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
    for subscription_uid in subscriptions:
        wirehome.message_bus.unsubscribe(subscription_uid)


def __button_callback__(message):
    command = {"type": "toggle"}

    for target_uid in config["targets"]:
        wirehome.component_registry.execute_command(target_uid, command)
