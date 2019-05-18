import datetime

config = {}


def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)

    return wirehome.response_creator.not_supported(type)


def process_adapter_message(message):
    type = message.get("type", None)

    if type == "value_received":
        key = message.get("key", None)

        if key == "counter":
            value = float(message.get("value", 0.0))
            divisor = float(config.get("divisor", 1.0))
            value = value / divisor

            wirehome.component.set_status("meter.value", value)

        elif key == "activity":
            value = message.get("value", None)
            value = value in ["True", "true", "1", True]

            wirehome.component.set_status("meter.is_active", value)

            if value:
                wirehome.component.set_status("meter.last_activity", datetime.datetime.now().isoformat())

        return wirehome.response_creator.success()

    return wirehome.response_creator.not_supported(type)


def __initialize__(message):
    wirehome.component.set_status("meter.value", "unknown")

    unit = config.get("unit", "m³")
    supports_activity = config.get("supports_activity", False)

    if supports_activity:
        wirehome.component.set_status("meter.is_active", False)

    wirehome.component.set_configuration("unit", unit)
    wirehome.component.set_configuration("app.view_source", wirehome.package_manager.get_file_uri(wirehome.context["logic_uid"], "appView.html"))

    return wirehome.publish_adapter_message({
        "type": "initialize"
    })
