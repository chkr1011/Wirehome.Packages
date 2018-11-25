def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return response_creator.success()

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def process_adapter_message(message):
    pass


def __initialize__(message):
    component.set_status("display.text", "")
    component.set_configuration("app.view_source", wirehome.package_manager.get_file_uri(scope["logic_uid"], "appView.html"))

    return publish_adapter_message({
        "type": "initialize"
    })
