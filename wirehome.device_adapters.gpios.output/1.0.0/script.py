config = {}


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()
    elif type == "turn_off":
        return __set_state__("off")
    elif type == "turn_on":
        return __set_state__("on")
    else:
        return {
            "type": "exception.not_supported",
            "origin_type": type
        }


def __initialize__():
    for gpio_definition in config["gpios"]:
        gpio_host_id = gpio_definition.get("host_id", "")
        gpio_id = gpio_definition.get("gpio_id", None)

        wirehome.gpio.set_direction(gpio_host_id, gpio_id, "out")

    return wirehome.response_creator.success()


def __set_state__(state):
    for gpio_definition in config["gpios"]:
        gpio_host_id = gpio_definition.get("host_id", "")
        gpio_is_inverted = gpio_definition.get("is_inverted", False)
        gpio_id = gpio_definition.get("gpio_id", None)

        gpio_state = "low"

        if state == "on":
            gpio_state = "high"

        if gpio_is_inverted == True:
            if gpio_state == "high":
                gpio_state = "low"
            else:
                gpio_state = "high"

        wirehome.gpio.set_state(gpio_host_id, gpio_id, gpio_state)

    return wirehome.response_creator.success()
