def initialize():
    pass


def activate():
    global subscriptions
    subscriptions = []

    __attach_button__(config["up_button"])
    __attach_button__(config["down_button"])
    

def deactivate():
    for subscription_uid in subscriptions:
        message_bus.unsubscribe(subscription_uid)


def __attach_button__(uid):
    filter = {
        "type": "component_registry.event.status_changed",
        "component_uid": uid,
        "status_uid": "button.state",
        "new_value": "pressed"
    }

    subscription_uid = scope["automation_uid"] + ":status_changed->" + uid
    message_bus.subscribe(subscription_uid, filter, __button_callback__)
    
    global subscriptions
    subscriptions.append(subscription_uid)


def __button_callback__(message):
    roller_shutter_uid = config["roller_shutter"]
    up_button_uid = config["up_button"]
    down_button_uid = config["down_button"]
    
    component_uid = message["component_uid"]
    up_is_pressed = component_uid == up_button_uid
    down_is_pressed = component_uid == down_button_uid

    current_state = component_registry.get_status(roller_shutter_uid, "roller_shutter.state")
    command = "turn_off"
    
    if up_is_pressed and current_state != "moving_up":
        command = "move_up"
    elif down_is_pressed and current_state != "moving_down":
        command = "move_down"

    component_registry.execute_command(roller_shutter_uid, {"type": command})