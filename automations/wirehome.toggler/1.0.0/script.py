def initialize():
    pass


def activate():
    global subscriptions
    subscriptions = []

    for button_uid in config["buttons"]:
        filter = {
            "type": "component_registry.event.status_changed",
            "component_uid": button_uid,
            "status_uid": "button.state",
            "new_value": "pressed"
        }

        subscription_uid = scope["automation_uid"] + ":status_changed->" + button_uid
        message_bus.subscribe(subscription_uid, filter, __button_callback__)
        subscriptions.append(subscription_uid)


def deactivate():
    for subscription_uid in subscriptions:
        message_bus.unsubscribe(subscription_uid)


def __button_callback__(message):
    command = {"type": "toggle"}

    for target_uid in config["targets"]:
        component_registry.execute_command(target_uid, command)
