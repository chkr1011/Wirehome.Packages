import time
import sys
import math

TIMER_ID = "wirehome.heating.monitor"

_is_running = False

_zones = []

_zone_status = {}

config = {}


class Zone:
    uid = None
    config = {}
    current_temperature = None
    target_temperature = None
    effective_target_temperature = None
    outdoor_temperature = None
    effective_outdoor_temperature = None
    affected_reduction = None
    valve_command = None
    status_reason = None
    low_delta_temperature = None
    low_delta_temperature_reached = False
    high_delta_temperature = None
    high_delta_temperature_reached = False
    error = None

# TODO: Rename reduction to "mode" and set one "forced_mode" via API.

def initialize():
    pass


def start():
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
    wirehome.scheduler.start_timer(TIMER_ID, monitoring_interval, __update__)

    global _is_running
    _is_running = True

    update() # Update now. We have to wait one full delay otherwise.


def stop():
    wirehome.scheduler.stop_timer(TIMER_ID)

    global _is_running
    _is_running = False


def get_status():
    return {
        "is_running": _is_running,
        "zone_status": _zone_status
    }


def update():
    # This method can be called via API to force update.
    __update__(None)


def __update__(_):
    for zone in _zones:
        __update_zone__(zone)

        global _zone_status
        _zone_status[zone.uid] = {
            "outdoor_temperature": zone.outdoor_temperature,
            "effective_outdoor_temperature": zone.effective_outdoor_temperature,
            "current_temperature": zone.current_temperature,
            "target_temperature": zone.target_temperature,
            "effective_target_temperature": zone.effective_target_temperature,
            "affected_reduction": zone.affected_reduction,
            "high_delta_temperature": zone.high_delta_temperature,
            "high_delta_temperature_reached": zone.high_delta_temperature_reached,
            "low_delta_temperature": zone.low_delta_temperature,
            "low_delta_temperature_reached": zone.low_delta_temperature_reached,
            "status_reason": zone.status_reason,
            "valve_command": zone.valve_command,
            "error": zone.error
        }


def __update_zone__(zone):
    try:
        wirehome.log.info("Updating heating zone '{uid}'.".format(uid=zone.uid))

        zone.error = None

        __fill_outdoor_temperature__(zone)
        __fill_affected_reduction__(zone)
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

    if zone.affected_reduction != None:
        zone.effective_target_temperature = zone.affected_reduction.get("target_temperature", 16)

    low_delta = zone.config.get("low_delta", 0.3)
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


def __fill_affected_reduction__(zone):
    # The zone reductions have priority. If no one of these is available or match
    # the global reductions become responsible.
    reductions = zone.config.get("reductions", {})
    (reduction_key, reduction) = __get_affected_reduction_internal__(reductions)

    if reduction_key != None:
        zone.affected_reduction = reduction

    reductions = config.get("reductions", {})
    (reduction_key, reduction) = __get_affected_reduction_internal__(reductions)

    if reduction_key != None:
        zone.affected_reduction = reduction


def __get_affected_reduction_internal__(reductions):
    now = time.strftime("%H:%M:%S")

    for reduction_key in reductions:
        reduction = reductions[reduction_key]

        begin = reduction.get("begin", "00:00:00")
        end = reduction.get("end", "23:59:59")

        if begin <= now and end >= now:
            return (reduction_key, reduction)

    return (None, None)
