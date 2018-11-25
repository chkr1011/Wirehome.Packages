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

        subscription_uid = context["automation_uid"] + ":status_changed->" + button_uid
        wirehome.message_bus.subscribe(subscription_uid, filter, __button_callback__)
        subscriptions.append(subscription_uid)


def deactivate():
    for subscription_uid in subscriptions:
        wirehome.message_bus.unsubscribe(subscription_uid)

    subscriptions.clear()


def __button_callback__(message):
    command = {"type": "toggle"}

    for target_uid in config["targets"]:
        wirehome.component_registry.execute_command(target_uid, command)
