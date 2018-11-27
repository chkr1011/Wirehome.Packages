config = {}


def initialize():
    pass


def activate():
    global subscriptions
    subscriptions = []
    global countdown_uid
    countdown_uid = context["automation_uid"] + ":countdown"

    for motion_detector_uid in config.get("motion_detectors", []):
        filter = {
            "type": "component_registry.event.status_changed",
            "component_uid": motion_detector_uid,
            "status_uid": "motion_detection.state"
        }

        subscription_uid = context["automation_uid"] + ":status_changed->" + motion_detector_uid
        wirehome.message_bus.subscribe(subscription_uid, filter, __motion_detector_callback__)
        subscriptions.append(subscription_uid)


def deactivate():
    global subscriptions
    for subscription_uid in subscriptions:
        wirehome.message_bus.unsubscribe(subscription_uid)

    subscriptions = []


def __motion_detector_callback__(properties):
    __restart_countdown__()

    if properties["new_value"] == "detected":
        __set_lights_state__("on")


def __countdown_callback__(_):
    for component_uid in config["motion_detectors"]:
        if wirehome.component_registry.get_status(component_uid, "motion_detection.state") == "detected":
            __restart_countdown__()
            return

    __set_lights_state__("off")


def __set_lights_state__(state):
    command = {}

    if state == "on":
        command = {"type": "turn_on"}
        custom_message = config.get("on_message", None)
        if custom_message != None:
            command = custom_message
    elif state == "off":
        command = {"type": "turn_off"}
        custom_message = config.get("off_message", None)
        if custom_message != None:
            command = custom_message

    for target_uid in config.get("targets", []):
        if __skip_condition_is_match__(target_uid):
            continue

        wirehome.component_registry.process_message(target_uid, command)


def __restart_countdown__():
    duration = config.get("duration", 5000)
    wirehome.scheduler.start_countdown(countdown_uid, duration, __countdown_callback__)


def __skip_condition_is_match__(component_uid):
    skip_status = config.get("skip_condition", {}).get("status", None)
    if skip_status == None:
        return False

    for status_uid in skip_status:
        status_value = skip_status[status_uid]
        current_status_value = wirehome.component_registry.get_status(component_uid, status_uid)

        if current_status_value != status_value:
            return False

    return True
