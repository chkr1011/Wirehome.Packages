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

    for button in config["buttons"]:
        __attach_button__(button)


def __disable__():
    for subscription_uid in subscriptions:
        wirehome.message_bus.unsubscribe(subscription_uid)


def __attach_button__(uid):
    filter = {
        "type": "component_registry.event.status_changed",
        "component_uid": uid,
        "status_uid": "button.state",
        "new_value": "pressed"
    }

    subscription_uid = wirehome.context["component_uid"] + ":status_changed->" + uid
    wirehome.message_bus.subscribe(subscription_uid, filter, __button_callback__)

    global subscriptions
    subscriptions.append(subscription_uid)


def __button_callback__(message):
    targets = config.get("targets", [])

    for target in targets:
        wirehome.component_registry.execute_command(target, {"type": "increase_level"})
