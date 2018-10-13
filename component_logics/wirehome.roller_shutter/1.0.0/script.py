def process_logic_message(message):
    type = message.get("type", None)

    if type == "initialize":
        return __initialize__(message)
    elif type == "turn_off":
        return __set_state__("turn_off")
    elif type == "move_up":
        return __set_state__("move_up")
    elif type == "move_down":
        return __set_state__("move_down")
    elif type == "set_position":
        return __set_position__(message)

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def process_adapter_message(message):
    pass


def __initialize__(message):
    global current_position
    current_position = 0
    global target_position
    target_position = None
    global current_state
    current_state = "unknown"
    global position_tracker_current
    position_tracker_current = 0
    global position_tracker_max
    position_tracker_max = globals().get("config", {}).get("max_position", 0)

    component.set_status("roller_shutter.state", "unknown")
    component.set_status("roller_shutter.position", "unknown")
    component.set_status("power.state", "unknown")
    component.set_status("power.consumption", "unknown")

    adapter_result = publish_adapter_message({
        "type": "initialize"
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    if position_tracker_max > 0:
        component_uid = scope["component_uid"]
        timer_uid = "wirehome.logic.roller_shutter.position_tracker:" + component_uid
        scheduler.start_timer(timer_uid, 250, __position_tracker_callback__)

    return __set_state__("turn_off")


def __set_state__(state):
    adapter_result = publish_adapter_message({
        "type": state
    })

    if adapter_result.get("type", None) != "success":
        return adapter_result

    # The power consumption from the adapter has a higher precedence (if supported and delivered)!
    power_consumption = adapter_result.get("power.consumption", None)

    if power_consumption == None:
        power_consumption = globals().get("config", {}).get("static_power_consumption", None)

    global current_state

    if state == "turn_off":
        component.set_status("roller_shutter.state", "off")
        component.set_status("roller_shutter.position", 0)
        component.set_status("power.state", "off")

        if power_consumption != None:
            component.set_status("power.consumption", 0)

        current_state = "off"

    if state == "move_up":
        component.set_status("roller_shutter.state", "moving_up")
        component.set_status("power.state", "on")

        if power_consumption != None:
            component.set_status("power.consumption", power_consumption)

        start_auto_off_countdown = True
        current_state = "moving_up"

    if state == "move_down":
        component.set_status("roller_shutter.state", "moving_down")
        component.set_status("power.state", "on")

        if power_consumption != None:
            component.set_status("power.consumption", power_consumption)

        start_auto_off_countdown = True
        current_state = "moving_down"

    auto_off_timeout = globals().get("config", {}).get("auto_off_timeout", 60000)
    start_auto_off_countdown = state == "move_up" or state == "move_down"

    if start_auto_off_countdown == True and auto_off_timeout != None:
        countdown_uid = scope["component_uid"] + ".auto_off"
        scheduler.start_countdown(countdown_uid, auto_off_timeout, __auto_off_callback__)

    return {"type": "success"}


def __auto_off_callback__(_):
    __set_state__("turn_off")


def __set_position__(message):
    global target_position
    target_position = message.get("position", 0)

    if target_position > current_position:
        return __set_state__("move_down")
    elif target_position < current_position:
        return __set_state__("move_up")

def __position_tracker_callback__(elapsed_time, state):
    if current_state == "off":
        return
    
    global position_tracker_current

    if current_state == "moving_up":    
        position_tracker_current -= elapsed_time
    elif current_state == "moving_down":
        position_tracker_current += elapsed_time

    if position_tracker_current < 0:
        position_tracker_current = 0
    elif position_tracker_current > position_tracker_max:
        position_tracker_current = position_tracker_max

    global current_position
    current_position = (position_tracker_current * 100) / position_tracker_max

    is_closed = current_position > 95

    component.set_status("roller_shutter.position", current_position)
    component.set_status("roller_shutter.is_closed", is_closed)
   
