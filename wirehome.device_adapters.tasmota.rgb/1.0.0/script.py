config = {}


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()
    elif type == "set_state":
        return __set_state__(message)
    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def __initialize__():
    return {
        "type": "success",
        "supports_brightness": True,
        "supports_color": True
    }


def __set_state__(state):
    topic = config["topic"]
    
    power_state = state.get("power_state")
    brightness = state.get("brightness", 100)
    color = state.get("color", "#ffffff")

    # Hints:
    # The device will also turn the light on when changing the brightness.
    # No value conversion is needed because Tasmota and Wirehome.Core are compatible.

    # Only update brightness and color only if the device will be on.
    # It is important to set the color first because the dimmer will
    # change the actual color value.
    if power_state == "off":
        mqtt_message = {
            "topic": "cmnd/" + topic + "/power",
            "payload": "off"
        }

        wirehome.mqtt.publish(mqtt_message)
        return {"type": "success"}

    mqtt_color_message = {
        "topic": "cmnd/" + topic + "/color",
        "payload": color
    }

    mqtt_brightness_message = {
        "topic": "cmnd/" + topic + "/dimmer",
        "payload": str(brightness)
    }

    wirehome.mqtt.publish(mqtt_color_message)
    wirehome.mqtt.publish(mqtt_brightness_message)

    return {"type": "success"}
