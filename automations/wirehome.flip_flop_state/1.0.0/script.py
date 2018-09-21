def initialize():
    pass


def activate():
    global subscriptions
    subscriptions = []

    for button_uid in config["buttons"]:
        event = config["buttons"][button_uid].get("event", "pressed")

        filter = {
            "type": "component_registry.event.status_changed",
            "component_uid": button_uid,
            "status_uid": "button.state",
            "new_value": event
        }

        subscription = message_bus.subscribe(filter, __button_callback__)
        subscriptions.append(subscription)


def deactivate():
    for subscription_uid in subscriptions:
        message_bus.unsubscribe(subscription_uid)


def __button_callback__(message):
    flip_state = config["flip_state"]
    flop_state = config["flop_state"]
    
    command = {
        "type": "set_state",
        "state": ""
    }

    for target_uid in config["targets"]:
        current_state = component_registry.get_status(target_uid, "state_machine.state")

        if current_state == flip_state:
            command["state"] = flop_state
        else:
            command["state"] = flip_state

        component_registry.execute_command(target_uid, command)
