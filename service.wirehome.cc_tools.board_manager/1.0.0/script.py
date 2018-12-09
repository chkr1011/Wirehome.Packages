from time import sleep

PARAMETER_DEVICE_UID = "device_uid"
PARAMETER_PORT = "port"
PARAMETER_STATE = "state"
PARAMETER_COMMIT = "commit"

BOARD_HS_REL_5 = "HSREL5"
BOARD_HS_REL_8 = "HSREL8"
BOARD_HS_PE_16_IN = "HSPE16-IN"
BOARD_HS_PE_16_OUT = "HSPE16-OUT"
BOARD_HS_PE_8_IN = "HSPE8-IN"
BOARD_HS_PE_8_OUT = "HSPE8-OUT"
BOARD_HS_RB_16 = "HSRB16"

config = {}

class Device:
    uid = ""
    bus_id = ""
    address = 0
    board = ""
    buffer = 0x0
    interrupt_gpio_host_id = ""
    interrupt_gpio_id = None
    fetch_mode = ""


def initialize():
    global devices
    devices = {}

    global devices_with_interrupt_polling
    devices_with_interrupt_polling = []

    global devices_with_state_polling
    devices_with_state_polling = []

    global output_devices
    output_devices = []

    global is_running
    is_running = False

    global message_bus_subscription
    message_bus_subscription = None

    global init_log
    init_log = []


def get_status():
    return {
        "init_log": init_log
    }


def start():
    __initialize_devices__()

    global is_running
    is_running = True

    filter = {
        "type": "gpio_registry.event.state_changed"
    }

    global message_bus_subscription
    uid = "wirehome.cc_tools.board_manager.gpio_state_changed"
    message_bus_subscription = wirehome.message_bus.subscribe(uid, filter, __handle_interrupt__)

    if len(devices_with_state_polling) > 0:
        wirehome.scheduler.start_thread("cc_tools.board_manager.poll_states", __poll_states_thread__)

    if len(devices_with_interrupt_polling) > 0:
        wirehome.scheduler.start_thread("cc_tools.board_manager.poll_interrupts", __poll_interrupts_thread__)


def stop():
    global is_running
    is_running = False

    if message_bus_subscription != None:
        wirehome.message_bus.unsubscribe(message_bus_subscription)


def commit_device_states():
    for device in output_devices:
        __write__state__(device)

    return {"type": "success"}


def set_state(parameters):
    device_uid = parameters["device_uid"]
    port = parameters["port"]
    state = parameters["state"]
    commit = parameters.get("commit", True)
    is_inverted = parameters.get("is_inverted", False)

    if is_inverted == True:
        if state == "closed":
            state = "open"
        elif state == "open":
            state = "closed"
        elif state == "high":
            state = "low"
        elif state == "low":
            state = "high"

    device = __get_device__(device_uid)
    state = __transform_port_state__(port, state, device.board)

    if state == "high":
        device.buffer |= 0x1 << port
    elif state == "low":
        device.buffer = ~(0x1 << port) & device.buffer

    if commit:
        __write__state__(device)

    return {
        "type": "success"
    }


def get_state(parameters):
    device_uid = parameters["device_uid"]
    port = parameters["port"]
    is_inverted = parameters.get("is_inverted", False)

    device = __get_device__(device_uid)
    state = (device.buffer & (0x1 << port)) > 0

    pin_state = "low"
    relay_state = "open"

    if state == True:
        pin_state = "high"
        relay_state = "closed"

    if is_inverted == True:
        if relay_state == "closed":
            relay_state = "open"
        elif relay_state == "open":
            relay_state = "closed"

        if pin_state == "high":
            pin_state = "low"
        elif pin_state == "low":
            pin_state = "high"

    if device.board == BOARD_HS_REL_5:
        if port >= 0 and port <= 4:
            if state == "high":
                relay_state = "open"
            elif state == "low":
                relay_state = "closed"

    return {
        "type": "success",
        "pin_state": pin_state,
        "relay_state": relay_state
    }


def __write__state__(device):
    if device.board == BOARD_HS_REL_5:
        __write_pcf8574__(device)
    elif device.board == BOARD_HS_REL_8:
        __write_max7311__(device)
    elif device.board == BOARD_HS_PE_8_OUT:
        __write_pcf8574__(device)
    elif device.board == BOARD_HS_PE_16_OUT:
        __write_max7311__(device)
    elif device.board == BOARD_HS_RB_16:
        __write_max7311__(device)


def __write_pcf8574__(device):
    wirehome.i2c.write_as_ulong(device.bus_id, device.address, device.buffer, 1)


def __write_max7311__(device):
    # byte 0 = Set target register to CONFIGURATION register
    # byte 1 = Set CONFIGURATION-1 to outputs
    # byte 2 = Set CONFIGURATION-2 to outputs
    buffer = [0x6, 0x0, 0x0]
    wirehome.i2c.write(device.bus_id, device.address, buffer)

    # byte 0 = Set target register to OUTPUT-1 register
    # byte 1 = The state of ports 0-7
    # byte 2 = The state of ports 8-15
    buffer = 0x2
    buffer |= device.buffer << 8
    wirehome.i2c.write_as_ulong(device.bus_id, device.address, buffer, 3)


def __transform_port_state__(port, port_state, board):
    if port_state == "high" or port_state == "low":
        return port_state

    if board == BOARD_HS_REL_5:
        if port_state == "closed":
            if port >= 0 and port <= 4:  # ports 0-4 are inverted by hardware
                return "low"
            else:
                return "high"
        elif port_state == "open":
            if port >= 0 and port <= 4:  # ports 0-4 are inverted by hardware
                return "high"
            else:
                return "low"

    if port_state == "closed":
        return "high"
    else:
        return "low"


def __get_device__(uid):
    return devices[uid]


def __initialize_devices__():
    global init_log

    devices = config["devices"]
    for device_uid in devices:
        device_config = devices[device_uid]

        init_log.append("Initializing " + device_uid)

        __initialize_device__(device_uid, device_config)


def __initialize_device__(device_uid, config):
    try:
        device = Device()
        device.uid = device_uid
        device.board = config["board"]
        device.bus_id = config.get("bus_id", "")
        device.address = config["address"]
        device.fetch_mode = config.get("fetch_mode", "")
        device.buffer = config.get("initial_state", 0)
        device.interrupt_gpio_host_id = config.get("interrupt_gpio_host_id", "")
        device.interrupt_gpio_id = config.get("interrupt_gpio_id", None)

        global devices_with_interrupt_polling
        global devices_with_state_polling

        if device.fetch_mode == "interrupt":
            if device.interrupt_gpio_id != None:
                wirehome.gpio.enable_interrupt(device.interrupt_gpio_host_id, device.interrupt_gpio_id)
        elif device.fetch_mode == "poll_interrupt":
            if device.interrupt_gpio_id != None:
                wirehome.gpio.set_direction(device.interrupt_gpio_host_id, device.interrupt_gpio_id, "in")
                devices_with_interrupt_polling.append(device)
        elif device.fetch_mode == "poll_state":
            devices_with_state_polling.append(device)

        if device.board == BOARD_HS_REL_5:
            # Initial state is all relays off (respecting the inverted pins)
            device.buffer = 0x1F

        if device.board == BOARD_HS_PE_16_IN:
            __initialize_input_hspe16__(device)

        __write__state__(device)

        global devices
        devices[device.uid] = device

        global output_devices
        if (device.board == BOARD_HS_REL_5 or
            device.board == BOARD_HS_REL_8 or
            device.board == BOARD_HS_PE_8_OUT or
            device.board == BOARD_HS_PE_16_OUT or
                device.board == BOARD_HS_RB_16):
            output_devices.append(device)

        print("Initialized device " + device.uid)
    except:
        print("Initializing device " + device.uid + " failed.")


def __initialize_input_hspe16__(device):
    buffer = [
        0x6,  # Set target register to CONFIGURATION register
        0xFF,  # Set CONFIGURATION-1 to inputs
        0xFF  # Set CONFIGURATION-2 to inputs
    ]

    wirehome.i2c.write(device.bus_id, device.address, buffer)

    __poll_state__(device)


def __handle_interrupt__(message):
    new_state = message["new_state"]

    if new_state != "low":
        return

    gpio_host_id = message["gpio_host_id"]
    gpio_id = message["gpio_id"]

    for device_uid in devices:
        device = devices[device_uid]

        if device.interrupt_gpio_host_id == gpio_host_id and device.interrupt_gpio_id == gpio_id:
            __poll_state__(device)


def __poll_interrupts_thread__(_):
    while is_running == True:
        sleep(0.010)  # 10 ms

        gpio_states = {}

        for device in devices_with_interrupt_polling:
            gpio_key = device.interrupt_gpio_host_id + str(device.interrupt_gpio_id)

            if not gpio_key in gpio_states:
                gpio_states[gpio_key] = wirehome.gpio.read_state(device.interrupt_gpio_host_id, device.interrupt_gpio_id)

            if gpio_states[gpio_key] == "low":
                __poll_state__(device)


def __poll_states_thread__(_):
    while is_running == True:
        sleep(0.100)  # 100 ms

        for device in devices_with_state_polling:
            __poll_state__(device)


def __poll_state__(device):
    new_state = None

    if device.board == BOARD_HS_PE_16_IN:
        # Set target register to INPUT-0 register and read two register bytes (INPUT-0 and INPUT-1)
        write_buffer = 0x0
        new_state = wirehome.i2c.write_read_as_ulong(device.bus_id, device.address, write_buffer, 1, 2)
    elif device.board == BOARD_HS_PE_8_IN:
        new_state = wirehome.i2c.read_as_ulong(device.bus_id, device.address, 1)

    if new_state == None:
        return

    old_state = device.buffer
    has_changed = old_state != new_state

    if has_changed == False:
        return

    device.buffer = new_state

    message = {
        "type": "cc_tools.board_manager.event.state_changed",
        "device_uid": device.uid,
        "new_state": new_state,
        "old_state": old_state
    }

    wirehome.message_bus.publish(message)
