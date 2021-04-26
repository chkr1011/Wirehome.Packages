import time
import json

wirehome = None
config = {}

def initialize():
    pass


def start():
    # TODO rename to adapter and restart!
    wirehome.message_bus.subscribe("homeassistant_bridge.state_forwarder.component_state_changing", { "type": "component_registry.event.status_changing" }, on_component_state_changing)
    wirehome.message_bus.subscribe("homeassistant_bridge.state_forwarder.component_state_changed", { "type": "component_registry.event.status_changed" }, on_component_state_changed)

    wirehome.mqtt.subscribe("homeassistant_bridge.command_receiver", "homeassistant_adapter/command/#", on_mqtt_command_received)

    publish_components()
    wirehome.scheduler.start_timer("homeassistant_bridge.publish", 300000, on_publish_timer_elapsed, None)


def publish_components():

    for component_uid in wirehome.component_registry.get_uids():
        try:
            if not wirehome.component_registry.is_initialized(component_uid):
                continue

            if wirehome.component_registry.has_status(component_uid, "temperature.value"):
                publish_sensor(component_uid, "temperature.value", "temperature", "°C", 180, 1)
                continue
            
            if wirehome.component_registry.has_status(component_uid, "humidity.value"):
                publish_sensor(component_uid, "humidity.value", "humidity", "%", 180, 0)
                continue

            if wirehome.component_registry.has_status(component_uid, "pressure.value"):
                publish_sensor(component_uid, "pressure.value", "pressure", "hPa", 180, 0)
                continue

            if wirehome.component_registry.has_status(component_uid, "motion_detection.state"):
                publish_binary_sensor(component_uid, "motion_detection.state", "motion")
                continue

            if wirehome.component_registry.has_status(component_uid, "roller_shutter.state"):
                publish_blind(component_uid)
                continue

            if wirehome.component_registry.has_status(component_uid, "window.state"):
                publish_window(component_uid)
                continue

            if wirehome.component_registry.has_status(component_uid, "level.current"): 
                publish_fan(component_uid)
                continue

            if wirehome.component_registry.has_status(component_uid, "button.state"): 
                publish_button(component_uid)
                continue

            if wirehome.component_registry.has_status(component_uid, "valve.state"): 
                publish_valve(component_uid)
                continue

            if wirehome.component_registry.has_status(component_uid, "power.state"): 
                if wirehome.component_registry.get_logic_id(component_uid) == "wirehome.logical_devices.lamp": 
                    publish_light(component_uid)
                    continue
                else:
                    publish_switch(component_uid)
                    continue
        except:
            pass


def stop():
    pass


def get_debug_infomation(_):
    return {
        
    }


def on_publish_timer_elapsed(parameters):
    publish_components()


def on_component_state_changing(message):
    component_uid = message.get("component_uid", None)
    if component_uid == None:
        return

    status_uid = message.get("status_uid", None)
    new_value = message.get("new_value", None)

    if status_uid == "temperature.value":
        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/temperature.value".format(component_uid=component_uid), 
            "payload": str(new_value),
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    if status_uid == "humidity.value":
        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/humidity.value".format(component_uid=component_uid), 
            "payload": str(new_value),
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    if status_uid == "pressure.value":
        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/pressure.value".format(component_uid=component_uid), 
            "payload": str(new_value),
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)


def on_component_state_changed(message):
    component_uid = message.get("component_uid", None)
    if component_uid == None:
        return

    status_uid = message.get("status_uid", None)
    new_value = message.get("new_value", None)

    if status_uid == "motion_detection.state":
        payload = "OFF"
        if new_value == "detected":
            payload = "ON"

        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/motion_detection.state".format(component_uid=component_uid), 
            "payload": payload,
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    if status_uid == "roller_shutter.state":
        # open, opening, closed or closing
        payload = "stopped"
        if new_value == "moving_up":
            payload = "opening"
        elif new_value == "moving_down":
            payload = "closing"

        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/roller_shutter.state".format(component_uid=component_uid), 
            "payload": payload,
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    if status_uid == "window.state":
        payload = "closed"
        if new_value == "open":
            payload = "open"

        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/window.state".format(component_uid=component_uid), 
            "payload": payload,
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    if status_uid == "level.current":
        payload = "OFF"
        if new_value > 0:
            payload = "ON"

        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/level.current".format(component_uid=component_uid), 
            "payload": payload,
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/level.current/percentage".format(component_uid=component_uid), 
            "payload": str(new_value),
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    if status_uid == "button.state":
        payload = "OFF"
        if new_value == "pressed":
            payload = "ON"

        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/button.state".format(component_uid=component_uid), 
            "payload": payload,
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    if status_uid == "valve.state":
        payload = "OFF"
        if new_value == "open":
            payload = "ON"

        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/valve.state".format(component_uid=component_uid), 
            "payload": payload,
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    if status_uid == "power.state":
        payload = "OFF"
        if new_value == "on":
            payload = "ON"

        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/power.state".format(component_uid=component_uid), 
            "payload": payload,
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)


def on_mqtt_command_received(message):
    topic = message.get("topic", None)
    payload = str(message.get("payload", ""))
    component_uid = topic.split("/")[2]
    status_uid = topic.split("/")[3]

    if status_uid == "power.state":
        message = {}

        if payload == "ON":
            message["type"] = "turn_on"
        else:
            message["type"] = "turn_off"

        wirehome.component_registry.process_message(component_uid, message)

    elif status_uid == "roller_shutter.state":
        message = {}

        if payload == "OPEN":
            message["type"] = "move_up"
        elif (payload == "CLOSE"):
            message["type"] = "move_down"
        else:
            message["type"] = "turn_off"

        wirehome.component_registry.process_message(component_uid, message)

    elif status_uid == "level.current":
        level = 0
        if payload == "ON":
            level = 1

        message = {
            "type": "set_level",
            "level": level
        }

        wirehome.component_registry.process_message(component_uid, message)

    elif status_uid == "level.current.percentage":
        message = {
            "type": "set_level",
            "level": int(payload)
        }

        wirehome.component_registry.process_message(component_uid, message)

    elif status_uid == "valve.state":
        message = {
            "type": "close"
        }

        if payload == "ON":
            message["type"] = "open"

        wirehome.component_registry.process_message(component_uid, message)


def publish_binary_sensor(component_uid, status_uid, device_class):   
    state_topic = "homeassistant_adapter/value/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)

    config = {
        "state_topic": state_topic,
        "device_class": device_class
    }

    publish("binary_sensor", component_uid, status_uid, config)


def publish_sensor(component_uid, status_uid, device_class, unit_of_measurement, expire_after, round):
    state_topic = "homeassistant_adapter/value/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)

    config = {
        "state_topic": state_topic,
        "unit_of_measurement": unit_of_measurement,
        "device_class": device_class,
        "value_template": "{{ value | round(" + str(round) + ") }}"
    }

    if expire_after > 0:
        config["expire_after"] = expire_after

    publish("sensor", component_uid, status_uid, config)


def publish_switch(component_uid):
    status_uid = "power.state"

    state_topic = "homeassistant_adapter/value/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)
    command_topic = "homeassistant_adapter/command/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)
    
    config = {
        "state_topic": state_topic,
        "command_topic": command_topic,
    }

    publish("switch", component_uid, status_uid, config)


def publish_light(component_uid):
    status_uid = "power.state"

    state_topic = "homeassistant_adapter/value/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)
    command_topic = "homeassistant_adapter/command/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)
    
    config = {
        "state_topic": state_topic,
        "command_topic": command_topic,
    }

    publish("light", component_uid, status_uid, config)


def publish_blind(component_uid):
    status_uid = "roller_shutter.state"

    state_topic = "homeassistant_adapter/value/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)
    command_topic = "homeassistant_adapter/command/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)
    
    config = {
        "device_class": "blind",
        "state_topic": state_topic,
        "command_topic": command_topic
    }

    publish("cover", component_uid, status_uid, config)


def publish_window(component_uid):
    status_uid = "window.state"

    state_topic = "homeassistant_adapter/value/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)
    
    config = {
        "device_class": "window",
        "state_topic": state_topic
    }

    publish("cover", component_uid, status_uid, config)


def publish_fan(component_uid):
    status_uid = "level.current"

    state_topic = "homeassistant_adapter/value/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)
    percentage_state_topic = state_topic + "/percentage"
    command_topic = "homeassistant_adapter/command/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)
    percentage_command_topic = command_topic + ".percentage"

    max_level = wirehome.component_registry.get_configuration(component_uid, "level.max", None)
    if max_level == None:
        return

    config = {
        "speed_range_min": 1,
        "speed_range_max": max_level,
        "state_topic": state_topic,
        "command_topic": command_topic,
        "percentage_state_topic": percentage_state_topic,
        "percentage_command_topic": percentage_command_topic
    }

    publish("fan", component_uid, status_uid, config)


def publish_button(component_uid):
    status_uid = "button.state"

    state_topic = "homeassistant_adapter/value/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)
    
    config = {
        "state_topic": state_topic
    }

    publish("binary_sensor", component_uid, status_uid, config)


def publish_valve(component_uid):
    status_uid = "valve.state"

    state_topic = "homeassistant_adapter/value/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)
    command_topic = "homeassistant_adapter/command/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)
    
    config = {
        "state_topic": state_topic,
        "command_topic": command_topic,
    }

    publish("switch", component_uid, status_uid, config)


def publish(domain, component_uid, status_uid, config):
    unique_id = ("wirehome_" + component_uid + "_" + status_uid).replace(".", "_")
    discovery_topic = "homeassistant/{domain}/{unique_id}/config".format(domain=domain, unique_id=unique_id)

    config["platform"] = "mqtt"
    config["unique_id"] = unique_id
    config["name"] = "wirehome.{component_uid}_{status_uid}".format(component_uid=component_uid, status_uid=status_uid)

    # Do not use a device!

    mqtt_message = {
        "topic": discovery_topic, 
        "payload": generate_json(config)
    }

    wirehome.mqtt.publish(mqtt_message)


def generate_json(value):
    return json.dumps(value, ensure_ascii=False)
