TIMER_ID = "wirehome.tradfri.gateway_manager.polling"

config = {}

from time import sleep
import sys
import json

_devices = {}
_gateway_is_connected = False

def initialize():
    # wirehome.debugger.enable()

    global _devices, _gateway_is_connected
    _devices = {}
    _gateway_is_connected = False


def start():
    wirehome.scheduler.start_timer(TIMER_ID, 2000, __poll_status__)


def stop():
    wirehome.scheduler.stop_timer(TIMER_ID)


def get_debug_infomation(_):
    return {
        "devices": _devices,
        "trace": wirehome.debugger.get_trace(),
        "gateway_is_connected": _gateway_is_connected
    }


def __find_device_id__(caption):
    for device_uid in _devices:
        if _devices[device_uid]["9001"] == caption:
            return int(device_uid)

    return None


def set_device_status(status):
    device_id = status.get("device_id", None)
    if device_id == None:
        device_caption = status.get("device_id", None)
        device_id = __find_device_id__(device_caption)

    if device_id == None:
        return {"type": "exception.parameter_invalid", "parameter_name": "device_id"}

    power_state = status.get("power_state", 0)
    brightness = status.get("brightness",  245)
    color = status.get("color", "ffffff")

    uri = "15001/" + str(device_id)
    data = {"5850": power_state}

    # Do not add other values if power is off. Otherwise the device will go on and off
    # e.g when chaning the brightness while the device is off.
    if power_state == 1:
        data["5851"] = brightness
        data["5706"] = color

    data = {"3311": [data]}

    payload = json.dumps(data)

    response = __execute_coap_request__("put", uri, payload)

    if response["status"] == "Changed":
        return {"type": "success"}
    
    return {"type": response["status"]}


def __poll_status__(_):
    global _gateway_is_connected, _devices

    response = None
    try:
        new_devices = {}

        response = __execute_coap_request__("get", "15001")
        device_ids = response["payload"]
        device_ids = json.loads(device_ids)

        for device_id in device_ids:
            response = __execute_coap_request__("get", "15001/" + str(device_id))
            new_devices[device_id] = json.loads(response["payload"])

        _gateway_is_connected = True
        __fire_events__(_devices, new_devices)
        _devices = new_devices
    except:
        _gateway_is_connected = False
        print("TRADFRI gateway pull failed. (Response=" + str(response) + ")")
        sleep(10)


def __fire_events__(old, new):
    if old == None or new == None:
        return

    for device_id in new:
        old_power_state = __get_device_status_value__(old, device_id, "5850")
        new_power_state = __get_device_status_value__(new, device_id, "5850")
        if old_power_state != new_power_state:
            wirehome.message_bus.publish({
                "type": "tradfri.gateway_manager.event.device_state_changed",
                "device_id": device_id,
                "property": "power_state",
                "old_state": "on" if old_power_state == 1 else "off",
                "new_state": "on" if new_power_state == 1 else "off"
            })

        old_brightness = __get_device_status_value__(old, device_id, "5851")
        new_brightness = __get_device_status_value__(new, device_id, "5851")
        if old_brightness != new_brightness:
            wirehome.message_bus.publish({
                "type": "tradfri.gateway_manager.event.device_state_changed",
                "device_id": device_id,
                "property": "brightness",
                "old_state": old_brightness,
                "new_state": new_brightness
            })

        old_color = __get_device_status_value__(old, device_id, "5706")
        new_color = __get_device_status_value__(new, device_id, "5706")
        if old_color != new_color:
            wirehome.message_bus.publish({
                "type": "tradfri.gateway_manager.event.device_state_changed",
                "device_id": device_id,
                "property": "color",
                "old_state": old_color,
                "new_state": new_color
            })


def __get_device_status_value__(source, device_id, status_id):
    device = source.get(device_id, None)
    if device == None:
        return None

    status = device.get("3311", None)
    if status == None:
        return None

    if not isinstance(status, list):
        return None

    if len(status) != 1:
        return None

    status = status[0]

    return status.get(status_id, None)


def __execute_coap_request__(method, uri, payload=""):
    address = config.get("gateway_address", None)
    identity = config.get("identity", "wirehome")
    psk = config.get("psk", None)

    request = {
        "client_uid": "tradfri_gateway_manager",
        "host": address,
        "identity": identity,
        "key": psk,
        "method": method,
        "path": uri,
        "payload": payload
    }

    response = wirehome.coap.request(request)
    #print(response)
    return response
