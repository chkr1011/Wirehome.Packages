import datetime
import time

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
    # wirehome.debugger.enable()
    __enable__()


def __enable__():
    global sunrise_last_executed, sunset_last_executed, hot_close_last_executed
    sunrise_last_executed = None
    sunset_last_executed = None
    hot_close_last_executed = None

    __timer_tick__(None)

    global timer_uid
    timer_uid = wirehome.context["component_uid"] + ".timer"
    wirehome.scheduler.start_timer(timer_uid, 60000, __timer_tick__)


def __disable__():
    wirehome.scheduler.stop_timer(timer_uid)


def get_debug_infomation(_):
    return {
        "trace": wirehome.debugger.get_trace()
    }


def __timer_tick__(_):
    wirehome.debugger.clear_trace()

    global sunrise_last_executed, sunset_last_executed, hot_close_last_executed

    today = datetime.datetime.today()
    now = today.time()

    command = None

    if __is_sunrise_affected__(now) and sunrise_last_executed != today.day:
        command = "move_up"
        sunrise_last_executed = today.day

    if __is_sunset_affected__(now) and sunset_last_executed != today.day:
        command = "move_down"
        sunset_last_executed = today.day

    if __is_outdoor_temperature_high__() and hot_close_last_executed != today.day:
        command = "move_down"
        hot_close_last_executed = today.day

    if command != None:
        if not __check_outdoor_temperature_is_low_(command):
            __invoke_roller_shutter__(command)


def __is_sunset_affected__(now):
    if wirehome.component.get_setting("close_on_sunset", True) == False:
        return False

    sunset_shift = wirehome.component.get_setting("sunset_shift", "00:00:00")
    sunset = __parse_time__("outdoor.sunset", sunset_shift)
    return now >= sunset


def __is_sunrise_affected__(now):
    if wirehome.component.get_setting("open_on_sunrise", True) == False:
        return False

    disabled_before = wirehome.component.get_setting("disabled_before", None)
    if disabled_before != None:
        disabled_before = datetime.datetime.strptime(disabled_before, '%H:%M').time()

        if now < disabled_before:
            wirehome.debugger.trace("disabled before is affected")
            return False

    sunrise_shift = wirehome.component.get_setting("sunrise_shift", "00:00:00")
    sunrise = __parse_time__("outdoor.sunrise", sunrise_shift)
    return now >= sunrise


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


def __check_outdoor_temperature_is_low_(command):
    min_temperature = wirehome.component.get_setting("min_outdoor_temperature", None)
    if min_temperature == None:
        return False

    outdoor_temperature = wirehome.global_variables.get("outdoor.temperature", None)
    if outdoor_temperature == None:
        return False

    is_low = float(outdoor_temperature) < float(min_temperature)

    if not is_low:
        return False

    message = ""

    # TODO: Use resource service for translation
    if command == "move_down":
        message = "Skipped closing roller shutters because outdoor temperature is low ({outdoor_temperature} °C)."
    elif command == "move_up":
        message = "Skipped opening roller shutters because outdoor temperature is low ({outdoor_temperature} °C)."

    wirehome.notifications.publish("information", message.format(outdoor_temperature=outdoor_temperature))

    return True


def __is_outdoor_temperature_high__():
    max_temperature = wirehome.component.get_setting("auto_close_outdoor_temperature", None)
    if max_temperature == None:
        return False

    outdoor_temperature = wirehome.global_variables.get("outdoor.temperature", None)
    if outdoor_temperature == None:
        return False

    return float(outdoor_temperature) > float(max_temperature)
