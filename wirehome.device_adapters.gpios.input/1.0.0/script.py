config = {}


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()
    else:
        return {
            "type": "exception.not_supported",
            "origin_type": type
        }


def __initialize__():
    gpio_host_id = config.get("gpio_host_id", "")
    gpio_id = config.get("gpio_id", None)

    wirehome.gpio.set_direction(gpio_host_id, gpio_id, "in")
    wirehome.gpio.enable_interrupt(gpio_host_id, gpio_id)

    global subscription_uid
    subscription_uid = wirehome.context["component_uid"] + ".interrupt"

    filter = {
        "type": "gpio_registry.event.state_changed",
        "gpio_host_id": gpio_host_id,
        "gpio_id": gpio_id
    }

    wirehome.message_bus.subscribe(subscription_uid, filter, __handle_interrupt__)

    return wirehome.response_creator.success()


def __handle_interrupt__(parameters):
    new_state = parameters.get("new_state", None)

    if config.get("is_inverted", False) == True:
        if new_state == "high":
            new_state = "low"
        else:
            new_state = "high"

    button_state = "released"

    if new_state == "high":
        button_state = "pressed"

    message = {
        "type": "state_changed",
        "new_state": button_state
    }

    publish_adapter_message(message)
