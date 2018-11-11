TIMER_ID = "wirehome.tradfri.gateway_manager.poll_thread"


from time import sleep
import sys


def initialize():
    # wirehome.debugger.enable()
    pass


def start():
    wirehome.http_server.register_route("x", "api/v1/service.wirehome.homebridge_adapter/{componentUid}/turnOn", __turn_on_handler__)
    wirehome.http_server.register_route("y", "api/v1/service.wirehome.homebridge_adapter/{componentUid}/turnOff", __turn_off_handler__)
    wirehome.http_server.register_route("z", "api/v1/service.wirehome.homebridge_adapter/{componentUid}/status", __get_status_handler__)

    __update_configuration__()
    pass


def stop():
    pass


def __update_configuration__():
    configuration = __generate_configuration__()

    file = open("~/.homebridge/config.json", "w")
    try:
        file.write(wirehome.json_serializer.serialize_indented(configuration))
    except:
        file.close()


def __generate_configuration__():
    return {
        "bridge": __generate_bridge_configuration__(),
        "accessories": __generate_accessories_configuration__()
    }


def __generate_bridge_configuration__():
    return {
        "name": "Wirehome.Core",
        "username": "57:69:72:65:68:6f",
        "pin": "6d6-52-e43",
        "port": 81
    }


def __generate_accessories_configuration__():
    accessories = []

    for component_uid in wirehome.component_registry.get_uids():
        caption = wirehome.component_registry.get_setting(component_uid, "app.caption", component_uid)

        accessory = {
            "accessory": "HTTP-SWITCH",
            "name": caption,
            "switchType": "stateful",
            "onUrl": "http://localhost:80/api/v1/service.wirehome.homebridge_adapter/{componentUid}/turnOn".format(componentUid=component_uid),
            "offUrl": "http://localhost:80/api/v1/service.wirehome.homebridge_adapter/{componentUid}/turnOff".format(componentUid=component_uid),
            "statusUrl": "http://localhost:80/api/v1/service.wirehome.homebridge_adapter/{componentUid}/status".format(componentUid=component_uid)
        }

        accessories.append(accessory)

    return accessories


def __turn_on_handler__(parameters):
    pass


def __turn_off_handler__(parameters):
    pass


def __get_status_handler__(parameters):
    pass


def get_status():
    return {}
