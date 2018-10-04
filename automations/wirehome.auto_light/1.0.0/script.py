def initialize():
    pass


def activate():
    global subscriptions
    subscriptions = []
    global countdown_uid
    countdown_uid = None

    # TODO: Add buttons

    for component_uid in config["motion_detectors"]:
        filter = {
            "type": "component_registry.event.status_changed",
            "component_uid": component_uid,
            "status_uid": "motion_detection.state"
        }

        subscription = message_bus.subscribe(filter, __motion_detector_callback__)
        subscriptions.append(subscription)


def deactivate():
    global subscriptions
    for subscription_uid in subscriptions:
        message_bus.unsubscribe(subscription_uid)


def __motion_detector_callback__(properties):
    __restart_countdown__()

    if properties["new_value"] == "detected":
        __set_lights_state__("on")


def __countdown_callback__(_):
    for component_uid in config["motion_detectors"]:
        if component_registry.get_status(component_uid, "motion_detection.state") == "detected":
            __restart_countdown__()
            return

    __set_lights_state__("off")


def __set_lights_state__(state):
    command = {"type": "turn_off"}

    if state == "on":
        command = {"type": "turn_on"}

    for target_uid in config["targets"]:
        component_registry.execute_command(target_uid, command)


def __restart_countdown__():
    global countdown_uid
    duration = config.get("duration", 5000)
    countdown_uid = scheduler.start_countdown(countdown_uid, duration, __countdown_callback__)
