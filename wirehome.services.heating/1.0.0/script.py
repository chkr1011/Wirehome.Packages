import datetime
import time
import sys
import math

TIMER_ID = "wirehome.heating.monitor"

_is_running = False
_is_enabled = True

_zones = []

_zone_status = {}

_last_update = None

config = {}


class Zone:
    uid = None
    config = {}
    current_temperature = None
    target_temperature = None
    effective_target_temperature = None
    outdoor_temperature = None
    effective_outdoor_temperature = None
    forced_mode = None
    affected_mode = None
    affected_mode_key = None
    valve_command = None
    status_reason = None
    low_delta_temperature = None
    low_delta_temperature_reached = False
    high_delta_temperature = None
    high_delta_temperature_reached = False
    error = None


def initialize():
    pass


def start():
    wirehome.app.register_panel({
        "uid": "heating_panel",
        "position_index": 2,
        "view_source": wirehome.package_manager.get_file_uri(wirehome.context["service_uid"], "appView.html")
    })

    wirehome.app.register_status_provider("heating", __get_heating_status__)

    global _zones
    zoneConfigs = config.get("zones", {})
    for zone_key in zoneConfigs:
        zoneConfig = zoneConfigs[zone_key]

        if not zoneConfig.get("is_enabled", True):
            continue

        zone = Zone()
        zone.uid = zone_key
        zone.config = zoneConfig
        _zones.append(zone)

    monitoring_interval = config.get("monitoring", {}).get("interval", 5000)
    wirehome.scheduler.start_timer(TIMER_ID, monitoring_interval, __update_callback__)

    global _is_running
    _is_running = True

    update()  # Update now. We have to wait one full delay otherwise.


def stop():
    wirehome.scheduler.stop_timer(TIMER_ID)

    global _is_running
    _is_running = False


def enable():
    global _is_enabled
    _is_enabled = True


def disable():
    global _is_enabled
    _is_enabled = False


def get_status():
    return {
        "is_running": _is_running,
        "zone_status": _zone_status,
        "last_update": _last_update,
        "is_enabled": _is_enabled,
    }


def update():
    if not _is_enabled:
        return

    for zone in _zones:
        __update_zone__(zone)

        global _zone_status
        _zone_status[zone.uid] = {
            "outdoor_temperature": zone.outdoor_temperature,
            "effective_outdoor_temperature": zone.effective_outdoor_temperature,
            "current_temperature": zone.current_temperature,
            "target_temperature": zone.target_temperature,
            "effective_target_temperature": zone.effective_target_temperature,
            "affected_mode": zone.affected_mode,
            "affected_mode_key": zone.affected_mode_key,
            "forced_mode": zone.forced_mode,
            "high_delta_temperature": zone.high_delta_temperature,
            "high_delta_temperature_reached": zone.high_delta_temperature_reached,
            "low_delta_temperature": zone.low_delta_temperature,
            "low_delta_temperature_reached": zone.low_delta_temperature_reached,
            "status_reason": zone.status_reason,
            "valve_command": zone.valve_command,
            "error": zone.error
        }

    global _last_update
    _last_update = datetime.datetime.now().isoformat()


def __update_callback__(_):
    update()


def __update_zone__(zone):
    try:
        wirehome.log.info("Updating heating zone '{uid}'.".format(uid=zone.uid))

        zone.error = None

        __fill_outdoor_temperature__(zone)
        __fill_affected_mode__(zone)
        __fill_target_temperature__(zone)
        __fill_window_status__(zone)
        __fill_current_temperature__(zone)

        valve_command = "close"

        if zone.target_temperature == "off":
            zone.status_reason = "manual_disable"
        elif zone.effective_outdoor_temperature != None and zone.effective_outdoor_temperature >= zone.high_delta_temperature:
            zone.status_reason = "outdoor_temperature_is_higher"
        elif zone.window_status != "closed":
            zone.status_reason = "window_open"
        elif zone.current_temperature == None:
            zone.status_reason = "current_temperature_invalid"
        elif zone.high_delta_temperature_reached:
            zone.status_reason = "high_delta_temperature_reached"
        elif zone.current_temperature < zone.high_delta_temperature and not zone.low_delta_temperature_reached:
            zone.status_reason = "low_delta_temperature_not_reached"
        else:
            valve_command = "open"
            zone.status_reason = "heating_required"

        zone.valve_command = valve_command

        __update_valves__(zone, valve_command)

    except:
        wirehome.log.error(sys.exc_info())
        zone.error = "error"  # sys.exc_info()[0]


def __fill_outdoor_temperature__(zone):
    outdoor_sensor_uid = config.get("outdoor", {}).get("temperature_sensor", None)
    if outdoor_sensor_uid == None:
        zone.outdoor_temperature = None
        zone.effective_outdoor_temperature = None
        return

    outdoor_temperature = wirehome.component_registry.get_status(outdoor_sensor_uid, "temperature.value", None)
    if outdoor_temperature == None:
        zone.outdoor_temperature = None
        zone.effective_outdoor_temperature = None
        return

    if math.isnan(outdoor_temperature):
        zone.outdoor_temperature = None
        zone.effective_outdoor_temperature = None
        return

    zone.outdoor_temperature = outdoor_temperature

    if wirehome.component_registry.get_status(outdoor_sensor_uid, "is_outdated", False):
        zone.outdoor_temperature = None

    delta = config.get("outdoor", {}).get("delta", 0)
    zone.effective_outdoor_temperature = zone.outdoor_temperature - delta


def __fill_target_temperature__(zone):
    zone.target_temperature = zone.config.get("target_temperature", 20)
    zone.effective_target_temperature = zone.target_temperature

    if zone.affected_mode != None:
        zone.effective_target_temperature = zone.affected_mode.get("target_temperature", 16)

    low_delta = zone.config.get("low_delta", 0.1)
    zone.low_delta_temperature = zone.effective_target_temperature - low_delta

    high_delta = zone.config.get("high_delta", 0.1)
    zone.high_delta_temperature = zone.effective_target_temperature - high_delta


def __fill_current_temperature__(zone):
    temperature_sensors = zone.config.get("temperature_sensors", {})

    current_temperature = None

    for sensor_key in temperature_sensors:
        temperature = wirehome.component_registry.get_status(sensor_key, "temperature.value", None)
        if temperature != None:
            if current_temperature == None or temperature < current_temperature:
                current_temperature = temperature

    if not math.isnan(current_temperature):
        zone.current_temperature = current_temperature
    else:
        zone.current_temperature = None

    if zone.current_temperature != None:
        zone.high_delta_temperature_reached = zone.current_temperature >= zone.high_delta_temperature

        if zone.current_temperature <= zone.low_delta_temperature:
            zone.low_delta_temperature_reached = True

        if zone.high_delta_temperature_reached:
            zone.low_delta_temperature_reached = False


def __update_valves__(zone, status):
    command = {"type": "close"}
    if (status == "open"):
        command = {"type": "open"}

    valves = zone.config.get("valves", {})
    for valve_key in valves:
        wirehome.component_registry.process_message(valve_key, command)


def __fill_window_status__(zone):
    windows = zone.config.get("windows", {})
    for window_key in windows:
        window_status = wirehome.component_registry.get_status(window_key, "window.state", None)

        if window_status == "open":
            zone.window_status = "open"
            return
        elif window_status == "tilt":
            zone.window_status = "tilt"
            return

    # Only return "closed" if all windows are closed. The system should turn off the heating
    # when any of the affected windows is not closed (tilt or completely open).
    zone.window_status = "closed"


def __fill_affected_mode__(zone):
    # Reset the mode first. Otherwise it will stay forever.
    zone.affected_mode = None
    zone.affected_mode_key = None

    # The zone modes have priority. If no one of these is available or match
    # the global modes become responsible.
    modes = zone.config.get("modes", {})
    (mode_key, mode) = __get_affected_mode_internal__(modes)

    if mode_key != None:
        zone.affected_mode = mode
        zone.affected_mode_key = mode_key

    modes = config.get("modes", {})
    (mode_key, mode) = __get_affected_mode_internal__(modes)

    if mode_key != None:
        zone.affected_mode = mode
        zone.affected_mode_key = mode_key


def __get_affected_mode_internal__(modes):
    now = time.strftime("%H:%M:%S")

    for mode_key in modes:
        mode = modes[mode_key]

        begin = mode.get("begin", "00:00:00")
        end = mode.get("end", "23:59:59")

        if begin > end:
            if now >= begin:
                return (mode_key, mode)
            elif now <= end:
                return (mode_key, mode)
        elif now >= begin and now <= end:
            return (mode_key, mode)

    return (None, None)


def __get_heating_status__():
    """
    This method generates all the information which is needed for the heating panel in the app.
    """

    status = {}
    status["last_update"] = _last_update
    status["is_enabled"] = _is_enabled

    zones = []
    for zone in _zones:
        zones.append({
            "uid": zone.uid,
            "status_reason": zone.status_reason,
            "current_temperature": zone.current_temperature,
            "effective_target_temperature": zone.effective_target_temperature,
            "valve_command": zone.valve_command
        })

    status["zones"] = zones

    return status
