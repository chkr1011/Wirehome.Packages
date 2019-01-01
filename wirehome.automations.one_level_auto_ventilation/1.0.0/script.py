config = {}


def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__()
    if type == "enable":
        return __enable__()
    if type == "disable":
        return __disable__()
    else:
        return wirehome.response_creator.not_supported(type)


def __initialize__():
    __enable__()


def __enable__():
    global subscriptions
    subscriptions = []
    global countdown_uid
    countdown_uid = None
    global current_level
    current_level = None

    for motion_detector in config["motion_detectors"]:
        filter = {
            "type": "component_registry.event.status_changed",
            "component_uid": motion_detector,
            "status_uid": "motion_detection.state"
        }

        subscription_uid = wirehome.context["component_uid"] + ":status_changed->" + motion_detector
        wirehome.message_bus.subscribe(subscription_uid, filter, __motion_detector_callback__)
        subscriptions.append(subscription_uid)


def __disable__():
    for subscription in subscriptions:
        wirehome.message_bus.unsubscribe(subscription)


def __motion_detector_callback__(message):
    __restart_countdown__()

    if message["new_value"] == "detected":
        target_level = config.get("target_level", 1)
        __set_level__(target_level)


def __countdown_callback__(_):
    for component_uid in config["motion_detectors"]:
        if wirehome.component_registry.get_status(component_uid, "motion_detection.state") == "detected":
            __set_level__(1)
            __restart_countdown__()
            return

    __set_level__(0)


def __set_level__(level):
    global current_level
    current_level = level

    command = {"type": "set_level", "level": level}

    for fan_uid in config["fans"]:
        wirehome.component_registry.execute_command(fan_uid, command)


def __restart_countdown__():
    duration = config.get("duration", 5000)

    global countdown_uid
    countdown_uid = wirehome.scheduler.start_countdown(countdown_uid, duration, __countdown_callback__)
