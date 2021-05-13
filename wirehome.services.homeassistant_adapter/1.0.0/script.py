import time
import json

wirehome = None
config = {}

def initialize():
    pass


def start():
    wirehome.message_bus.subscribe("homeassistant_adapter.state_forwarder.component_state_changing", { "type": "component_registry.event.status_changing" }, on_component_state_changing)
    wirehome.message_bus.unsubscribe("homeassistant_adapter.state_forwarder.component_state_changed")

    wirehome.mqtt.subscribe("homeassistant_adapter.command_receiver", "homeassistant_adapter/command/#", on_mqtt_command_received)

    publish_components()
    wirehome.scheduler.start_timer("homeassistant_adapter.publish", 300000, on_publish_timer_elapsed, None)


def publish_components():

    for component_uid in wirehome.component_registry.get_uids():
        if not wirehome.component_registry.is_initialized(component_uid):
            continue

        # Publish sensors
        if wirehome.component_registry.has_status(component_uid, "temperature.value"):
            publish_sensor(component_uid, "temperature.value", "temperature", "°C", 240, 1)
        
        if wirehome.component_registry.has_status(component_uid, "humidity.value"):
            publish_sensor(component_uid, "humidity.value", "humidity", "%", 240, 0)

        if wirehome.component_registry.has_status(component_uid, "pressure.value"):
            publish_sensor(component_uid, "pressure.value", "pressure", "hPa", 240, 0)

        if wirehome.component_registry.has_status(component_uid, "meter.value"):
            publish_sensor(component_uid, "meter.value", None, "m³", 240, 3)

        if wirehome.component_registry.has_status(component_uid, "meter.is_active"):
            publish_binary_sensor(component_uid, "meter.is_active", "heat")
            
        if wirehome.component_registry.has_status(component_uid, "motion_detection.state"):
            publish_binary_sensor(component_uid, "motion_detection.state", "motion")
            
        if wirehome.component_registry.has_status(component_uid, "window.state"):
            publish_window(component_uid)
            
        if wirehome.component_registry.has_status(component_uid, "button.state"): 
            publish_button(component_uid)
            
        # Publish actuators
        if wirehome.component_registry.has_status(component_uid, "roller_shutter.state"):
            publish_roller_shutter(component_uid)
            
        if wirehome.component_registry.has_status(component_uid, "level.current"): 
            publish_fan(component_uid)
            
        if wirehome.component_registry.has_status(component_uid, "valve.state"): 
            publish_valve(component_uid)
            
        if wirehome.component_registry.has_status(component_uid, "power.state"): 
            if wirehome.component_registry.get_logic_id(component_uid) == "wirehome.logical_devices.lamp": 
                publish_light(component_uid)
            else:
                publish_switch(component_uid)

        publish_component_states(component_uid)


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

    #publish_state(component_uid, status_uid, new_value)

    publish_component_states(component_uid)


def publish_component_states(component_uid):
    if not wirehome.component_registry.is_initialized(component_uid):
        return

    #
    # Temperature > Value
    #
    temperature_value = wirehome.component_registry.get_status(component_uid, "temperature.value", None)
    if temperature_value != None:
        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/temperature.value".format(component_uid=component_uid), 
            "payload": str(temperature_value),
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    #
    # Humidity > Value
    #
    humidity_value = wirehome.component_registry.get_status(component_uid, "humidity.value", None)
    if humidity_value != None:
        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/humidity.value".format(component_uid=component_uid), 
            "payload": str(humidity_value),
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    #
    # Pressure > Value
    #
    pressure_value = wirehome.component_registry.get_status(component_uid, "pressure.value", None)
    if pressure_value != None:
        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/pressure.value".format(component_uid=component_uid), 
            "payload": str(pressure_value),
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    #
    # Motion detection > State
    #
    motion_detection_state = wirehome.component_registry.get_status(component_uid, "motion_detection.state", None)
    if motion_detection_state != None:
        payload = "OFF"
        if motion_detection_state == "detected":
            payload = "ON"

        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/motion_detection.state".format(component_uid=component_uid), 
            "payload": payload,
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    #
    # Meter > Value
    #
    meter_value = wirehome.component_registry.get_status(component_uid, "meter.value", None)
    if meter_value != None:
        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/meter.value".format(component_uid=component_uid), 
            "payload": str(meter_value),
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)
        
    #
    # Meter > Is active
    #
    meter_is_active = wirehome.component_registry.get_status(component_uid, "meter.is_active", None)
    if meter_is_active != None:
        payload = "OFF"
        if meter_is_active == True:
            payload = "ON"

        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/meter.is_active".format(component_uid=component_uid), 
            "payload": payload,
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    #
    # Roller Shutter > State
    #
    roller_shutter_state = wirehome.component_registry.get_status(component_uid, "roller_shutter.state", None)
    if roller_shutter_state != None:
        # open, opening, closed or closing
        payload = "stopped"
        if roller_shutter_state == "moving_up":
            payload = "opening"
        elif roller_shutter_state == "moving_down":
            payload = "closing"

        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/roller_shutter.state".format(component_uid=component_uid), 
            "payload": payload,
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    #
    # Window > State
    #
    window_state = wirehome.component_registry.get_status(component_uid, "window.state", None)
    if window_state != None:
        payload = "OFF"
        if window_state == "open":
            payload = "ON"

        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/window.state".format(component_uid=component_uid), 
            "payload": payload,
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

        payload = "OFF"
        if window_state == "tilt":
            payload = "ON"

        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/window.state.tilt".format(component_uid=component_uid), 
            "payload": payload,
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    #
    # Window > State
    #
    level_current = wirehome.component_registry.get_status(component_uid, "level.current", None)
    if level_current != None:
        payload = "OFF"
        if level_current > 0:
            payload = "ON"

        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/level.current".format(component_uid=component_uid), 
            "payload": payload,
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/level.current/percentage".format(component_uid=component_uid), 
            "payload": str(level_current),
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    #
    # Button > State
    #
    button_state = wirehome.component_registry.get_status(component_uid, "button.state", None)
    if button_state != None:
        payload = "OFF"
        if button_state == "pressed":
            payload = "ON"

        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/button.state".format(component_uid=component_uid), 
            "payload": payload,
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    #
    # Valve > State
    #
    valve_state = wirehome.component_registry.get_status(component_uid, "valve.state", None)
    if valve_state != None:
        payload = "OFF"
        if valve_state == "open":
            payload = "ON"

        mqtt_message = {
            "topic": "homeassistant_adapter/value/{component_uid}/valve.state".format(component_uid=component_uid), 
            "payload": payload,
            "retain": True
        }

        wirehome.mqtt.publish(mqtt_message)

    #
    # Power > State
    #
    power_state = wirehome.component_registry.get_status(component_uid, "power.state", None)
    if power_state != None:
        payload = "OFF"
        if power_state == "on":
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
        "value_template": "{{ value | round(" + str(round) + ") }}"
    }

    if device_class != None:
        config["device_class"] = device_class

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


def publish_roller_shutter(component_uid):
    status_uid = "roller_shutter.state"

    state_topic = "homeassistant_adapter/value/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)
    command_topic = "homeassistant_adapter/command/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)
    
    config = {
        "device_class": "shutter",
        "state_topic": state_topic,
        "command_topic": command_topic,

        # The position is faked in order to enable all control buttons!
        "position_topic": state_topic,
        "position_template": "{{ 50 }}",
    }

    publish("cover", component_uid, status_uid, config)


def publish_window(component_uid):
    status_uid = "window.state"

    state_topic = "homeassistant_adapter/value/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)
    
    config = {
        "device_class": "window",
        "state_topic": state_topic
    }

    publish("binary_sensor", component_uid, status_uid, config)

    status_uid = "window.state.tilt"
    state_topic = "homeassistant_adapter/value/{component_uid}/{status_uid}".format(component_uid=component_uid, status_uid=status_uid)
    
    config = {
        "device_class": "window",
        "state_topic": state_topic
    }

    publish("binary_sensor", component_uid, status_uid, config)


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
