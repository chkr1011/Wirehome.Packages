import datetime


def initialize():
    wirehome.debugger.enable()

    global pump_last_turned_on, countdown_uid, subscriptions

    pump_last_turned_on = None
    subscriptions = []
    countdown_uid = context["automation_uid"] + ":countdown"


def activate():
    global subscriptions

    for trigger_uid in config.get("triggers", []):
        if wirehome.component_registry.has_status(trigger_uid, "motion_detection.state"):
            filter = {
                "type": "component_registry.event.status_changed",
                "component_uid": trigger_uid,
                "status_uid": "motion_detection.state",
                "new_value": "detected"
            }

            subscription_uid = context["automation_uid"] + ":status_changed->" + trigger_uid
            wirehome.message_bus.subscribe(subscription_uid, filter, __motion_detector_callback__)
            subscriptions.append(subscription_uid)


def deactivate():
    for subscription_uid in subscriptions:
        wirehome.message_bus.unsubscribe(subscription_uid)


def get_status():
    return {
        "is_disabled_range_affected": __is_disabled_range_affected__(),
        "is_pause_active": __is_pause_active__(),
        "is_on": wirehome.scheduler.countdown_exists(countdown_uid),
        "trace": wirehome.debugger.get_trace()
    }


def __motion_detector_callback__(message):
    __try_turn_pump_on__()


def __try_turn_pump_on__():
    global pump_last_turned_on

    wirehome.debugger.clear_trace()

    if wirehome.scheduler.countdown_exists(countdown_uid):
        wirehome.debugger.trace("Countdown exists.")
        return

    if __is_pause_active__():
        wirehome.debugger.trace("Pause is active.")
        return

    if __is_disabled_range_affected__():
        wirehome.debugger.trace("Disabled by range.")
        return

    __start_countdown__()
    __set_pump_state__("on")
    
    pump_last_turned_on = datetime.datetime.now()


def __start_countdown__():
    duration = config.get("duration", 60)

    # The duration is defined as seconds.
    duration = duration * 1000

    wirehome.scheduler.start_countdown(countdown_uid, duration, __turn_pump_off_callback__)


def __turn_pump_off_callback__(_):
    __set_pump_state__("off")


def __set_pump_state__(state):
    component_uid = config.get("pump_uid", None)
    command = {"type": "turn_off"}

    if state == "on":
        command = {"type": "turn_on"}

    wirehome.debugger.trace("Sending command {command} to pump '{component_uid}'.".format(command=command, component_uid=component_uid))
    wirehome.component_registry.process_message(component_uid, command)


def __is_pause_active__():
    if pump_last_turned_on == None:
        return False

    pause = config["pause"]

    diff = datetime.datetime.now() - pump_last_turned_on
    pause = datetime.timedelta(seconds=pause)
    return diff < pause


def __is_disabled_range_affected__():
    range = config.get("disabled_range", None)
    if range == None:
        return False

    range_start = range.get("start", None)
    range_end = range.get("end", None)

    if range_start == None or range_end == None:
        return False

    range_start = datetime.datetime.strptime(range_start, "%H:%M").time()
    range_end = datetime.datetime.strptime(range_end, "%H:%M").time()
    now = datetime.datetime.now().time()

    in_range = __time_is_in_range__(range_start, range_end, now)
    wirehome.debugger.trace("Disabled check: range={start} - {end}; now={now}; in_range={in_range}".format(start=range_start, end=range_end, now=now, in_range=in_range))

    return in_range


def __time_is_in_range__(start, end, time):
    if start <= end:
        return start <= time <= end
    else:
        return start <= time or time <= end
