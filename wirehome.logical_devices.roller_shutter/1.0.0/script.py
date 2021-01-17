import datetime

class PositionTrackerStatus:
    current_position = 0
    position_tracker_max = None
    position_tracker_current = 0
    target_position = None

config = {}
position_tracker_status = PositionTrackerStatus()
current_state = None

def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)
    elif type == "turn_off":
        return __set_state__("turn_off")
    elif type == "disable":
        return __disable__()
    elif type == "enable":
        return __enable__()
    elif type == "move_up":
        return __set_state__("move_up")
    elif type == "move_down":
        return __set_state__("move_down")
    elif type == "set_position":
        return __set_position__(message)

    return wirehome.response_creator.not_supported(type)


def process_adapter_message(message):
    pass


def __initialize__(message):
    global position_tracker_status
    position_tracker_status.current_position = None
    position_tracker_status.position_tracker_current = None
    position_tracker_status.target_position = None
    position_tracker_status.position_tracker_max = config.get("max_position", None)

    global current_state
    current_state = None

    wirehome.component.set_status("roller_shutter.state", current_state)
    wirehome.component.set_status("roller_shutter.position", None)
    wirehome.component.set_status("roller_shutter.last_action", None)
    wirehome.component.set_status("power.state", None)
    wirehome.component.set_status("power.consumption", None)
    wirehome.component.set_configuration("app.view_source", wirehome.package_manager.get_file_uri(wirehome.context["logic_uid"], "appView.html"))

    adapter_result = publish_adapter_message({
        "type": "initialize"
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    return __set_state__("turn_off")


def __set_state__(command):
    # Skip if roller shutter is disabled.
    is_enabled = wirehome.component.get_setting("is_enabled", True)
    if not is_enabled:
        return wirehome.response_creator.disabled()

    # Perform requested operation at adapter level.
    adapter_result = wirehome.publish_adapter_message({
        "type": command
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    # The power consumption from the adapter has a higher precedence (if supported and delivered)!
    power_consumption = adapter_result.get("power.consumption", None)

    if power_consumption == None:
        power_consumption = config.get("static_power_consumption", None)

    global current_state
    global position_tracker_status

    final_state = "off"
    final_power_state = "off"
    final_power_consumption = power_consumption

    if command == "turn_off":
        if power_consumption != None:
            # Set 0 because the roller shutter is off. The real value is only used when
            # the roller shutter is moving into any direction.
            final_power_consumption = 0

    elif command == "move_up":
        final_state = "moving_up"
        final_power_state = "on"

    elif command == "move_down":
        final_state = "moving_down"
        final_power_state = "on"

    # START POSITION TRACKING TIMER.
    #component_uid = wirehome.context["component_uid"]
    #timer_uid = "wirehome.logic.roller_shutter.position_tracker:" + component_uid
    #if final_power_state == "on" and position_tracker_status.position_tracker_max != None:
    #    wirehome.scheduler.start_timer(timer_uid, 100, __position_tracker_callback__)
    #else:
    #    wirehome.scheduler.stop_timer(timer_uid)

    wirehome.component.set_status("roller_shutter.state", final_state)
    wirehome.component.set_status("roller_shutter.last_action", datetime.datetime.now().isoformat())
    wirehome.component.set_status("power.state", final_power_state)
    wirehome.component.set_status("power.consumption", final_power_consumption)
    
    auto_off_timeout = config.get("auto_off_timeout", 60000)
    start_auto_off_countdown = final_state != "off"

    if start_auto_off_countdown == True and auto_off_timeout != None:
        countdown_uid = wirehome.context["component_uid"] + ".auto_off"
        wirehome.scheduler.start_countdown(countdown_uid, auto_off_timeout, __auto_off_callback__)

    return wirehome.response_creator.success()


def __auto_off_callback__(_):
    __set_state__("turn_off")


def __set_position__(message):
    global position_tracker_status
    position_tracker_status.target_position = message.get("position", 0)

    if position_tracker_status.target_position > position_tracker_status.current_position:
        return __set_state__("move_down")
    elif position_tracker_status.target_position < position_tracker_status.current_position:
        return __set_state__("move_up")


def __position_tracker_callback__(parameters):
    if current_state != "moving_up" and current_state != "moving_down":
        return

    elapsed_time = parameters["elapsed_millis"]

    global position_tracker_status

    if current_state == "moving_up":
        position_tracker_status.position_tracker_current -= elapsed_time
    elif current_state == "moving_down":
        position_tracker_status.position_tracker_current += elapsed_time

    if position_tracker_status.position_tracker_current < 0:
        position_tracker_current = 0
    elif position_tracker_current > position_tracker_status.position_tracker_max:
        position_tracker_current = position_tracker_status.position_tracker_max

    new_current_position = (position_tracker_current * 100) / position_tracker_status.position_tracker_max

    if position_tracker_status.current_position == new_current_position:
        return

    current_position = new_current_position

    if current_position > 100:
        current_position = 100

    if current_position < 0:
        current_position = 0

    is_closed = current_position > 95

    wirehome.component.set_status("roller_shutter.position", current_position)
    wirehome.component.set_status("roller_shutter.is_closed", is_closed)


def __disable__():
    wirehome.component.set_setting("is_enabled", False)

    return wirehome.response_creator.success()


def __enable__():
    wirehome.component.set_setting("is_enabled", True)

    return wirehome.response_creator.success()