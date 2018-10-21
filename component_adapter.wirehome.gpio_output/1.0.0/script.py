def process_adapter_message(message):
    type = message.get("type", "")

    if type == "initialize":
        return __initialize__()
    elif type == "turn_off":
        return __set_state__("off")
    elif type == "turn_on":
        return __set_state__("on")
    else:
        return {
            "type": "not_supported",
            "origin_type": type
        }


def __initialize__():
    return { "type": "success" }
    

def __set_state__(state):
    for gpio_definition in config["gpios"]:
        gpio_host_id = gpio_definition.get("host_id", "")
        gpio_id = gpio_definition["gpio_id"]
        
        gpio_state = "low"

        if state == "on":
            gpio_state = "high"

        if gpio_definition.get("is_inverted", False) == True:
            if gpio_state == "high":
                gpio_state = "low"
            else:
                gpio_state = "high"
            
        gpio.set_direction(gpio_host_id, gpio_id, "out", gpio_state)
        #gpio.set_state(gpio_host_id, gpio_id, gpio_state)
        
    return { "type": "success" }
