def initialize():
    pass


def activate():
    global subscriptions
    subscriptions = []
    global countdown_uid
    countdown_uid = None
    global current_level 
    current_level = None

    for component_uid in config["motion_detectors"]:
        filter = {
            "type": "component_registry.event.status_changed",
            "component_uid": component_uid,
            "status_uid": "motion_detection.state"
        }

        subscription = message_bus.subscribe(filter, __motion_detector_callback__)
        subscriptions.append(subscription)


def deactivate():
    for subscription_uid in subscriptions:
        message_bus.unsubscribe(subscription_uid)


def __motion_detector_callback__(properties):
    __restart_countdown__()

    if properties["new_value"] == "detected":
        __set_level__(1)


def __countdown_callback__(uid):
    for component_uid in config["motion_detectors"]:
        if component_registry.get_status(component_uid, "motion_detection.state") == "detected":
            __set_level__(1)
            __restart_countdown__()
            return

    if current_level == 1:
        __set_level__(2)
        __restart_countdown__()
    else:
        __set_level__(0)


def __set_level__(level):
    global current_level
    current_level = level

    command = {"type": "set_level", "level": level}

    for target_uid in config["fans"]:
        component_registry.execute_command(target_uid, command)


def __restart_countdown__():
    global countdown_uid

    if current_level == 1:
        duration = config.get("second_level_duration", 5000)
    else:
        # Use first level duration when level is 0 (off) or already 2.
        duration = config.get("first_level_duration", 5000)

    countdown_uid = scheduler.start_countdown(countdown_uid, duration, __countdown_callback__)
