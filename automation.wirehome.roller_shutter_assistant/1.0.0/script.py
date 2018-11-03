import datetime
import time


def initialize():
    # wirehome.debugger.enable()
    pass


def activate():
    global sunrise_last_executed_day, sunset_last_executed_day
    sunrise_last_executed_day = None
    sunset_last_executed_day = None

    global timer_uid
    timer_uid = wirehome.context["automation_uid"] + ".timer"
    wirehome.scheduler.start_timer(timer_uid, 60000, __timer_tick__)

    __timer_tick__(None)


def deactivate():
    wirehome.scheduler.stop_timer(timer_uid)


def get_status():
    return {
        "trace": wirehome.debugger.get_trace()
    }


def __timer_tick__(_):
    wirehome.debugger.clear_trace()

    today = datetime.datetime.today()
    now = today.time()

    if sunset_last_executed_day != today.day:
        __invoke_sunset__(now, today.day)
    elif sunrise_last_executed_day != today.day:
        __invoke_sunrise__(now, today.day)


def __invoke_sunset__(now, day):
    close_on_sunset = wirehome.automation.get_setting("close_on_sunset", True)

    if close_on_sunset == False:
        return

    sunset_shift = wirehome.automation.get_setting("sunset_shift", "00:00:00")
    sunset = __parse_time__("outdoor.sunset", sunset_shift)
    sunset_is_affected = now >= sunset

    if not sunset_is_affected:
        return

    global sunset_last_executed_day
    sunset_last_executed_day = day

    if not __outdoor_temperature_is_ok__():
        # TODO: Add method and add more details. (Consider adding details for notifications in general and use resources.)
        wirehome.notifications.publish("information", "Skipped closing roller shutters because outdoor temperature is low.")
    else:
        __invoke_roller_shutter__("move_down")


def __invoke_sunrise__(now, day):
    open_on_sunrise = wirehome.automation.get_setting("open_on_sunrise", True)

    if open_on_sunrise == False:
        return

    disabled_before = wirehome.automation.get_setting("disabled_before", None)
    if disabled_before != None:
        disabled_before = datetime.datetime.strptime(disabled_before, '%H:%M').time()

        if disabled_before > now:
            wirehome.debugger.trace("disabled before is affected")
            return

    sunrise_shift = wirehome.automation.get_setting("sunrise_shift", "00:00:00")
    sunrise = __parse_time__("outdoor.sunrise", sunrise_shift)
    sunrise_is_affected = now >= sunrise

    if not sunrise_is_affected:
        return

    global sunrise_last_executed_day
    sunrise_last_executed_day = day

    if not __outdoor_temperature_is_ok__():
        # TODO: Add method and add more details. (Consider adding details for notifications in general and use resources.)
        wirehome.notifications.publish("information", "Skipped opening roller shutters because outdoor temperature is low.")
    else:
        __invoke_roller_shutter__("move_up")


def __invoke_roller_shutter__(command):
    for roller_shutter_uid in config.get("roller_shutters", []):
        wirehome.debugger.trace("invoking " + command + " for " + roller_shutter_uid)
        wirehome.component_registry.process_message(roller_shutter_uid, {"type": command})


def __parse_time__(global_variable_name, shift):
    value = wirehome.global_variables.get(global_variable_name)
    value = datetime.datetime.strptime(value, '%H:%M:%S')

    shift_is_negative = shift.startswith("-")
    if shift_is_negative:
        shift = shift[1:]

    shift = datetime.datetime.strptime(shift, '%H:%M:%S')
    shift = datetime.timedelta(hours=shift.hour, minutes=shift.minute, seconds=shift.second)

    if not shift_is_negative:
        value = value + shift
    else:
        value = value - shift

    return value.time()


def __outdoor_temperature_is_ok__():
    min_outdoor_temperature = wirehome.automation.get_setting("min_outdoor_temperature", None)
    if min_outdoor_temperature == None:
        return True

    outdoor_temperature = wirehome.global_variables.get("outdoor_temperature", None)
    if outdoor_temperature == None:
        return True

    outdoor_temperature = float(outdoor_temperature)
    return outdoor_temperature >= min_outdoor_temperature
