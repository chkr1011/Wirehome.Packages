def process_adapter_message(properties):
    type = properties.get("type", None)

    if type == "initialize":
        return __initialize__()
    elif type == "turn_on":
        return __turn_on__()
    elif type == "turn_off":
        return __turn_off__()

    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def __initialize__():
    return __turn_off__()


def __turn_on__():
    return __set_state__("on")


def __turn_off__():
    return __set_state__("off")


def __set_state__(state):
    device_id = config.get("device_id", None)
    if device_id == None:
        # TODO: lookup device id
        pass

    uri = "15001/{}".format(device_id)

    if state == "on":
        payload = "{\"3311\":[{\"5850\":1}]}"
    elif state == "off":
        payload = "{\"3311\":[{\"5850\":0}]}"

    return __execute_coap_request__("put", uri, payload)


def __execute_coap_request__(method, uri, payload):
    # TODO: Move to service using the function pool.
    gateway_address = config.get("gateway_address", None)
    uri = "coaps://{}:5684/{}".format(gateway_address, uri)

    # Implement a process to get a token and store it (adapter storage etc. Adapter.json)
    coap_client = config.get("coap_client_filename", "coap-client")
    client_identity = "Wirehome.Core"
    psk = config.get("psk")

    escapedPayload = payload.replace('"', '""')
    arguments = '-c "{} -m {} -u "{}" -k "{}" -e \'{}\' "{}""'.format(
        coap_client,
        method,
        client_identity,
        psk,
        escapedPayload,
        uri)

    log.debug("Tradfri adapter: {}".format(arguments))

    parameters = {
        "file_name": "/bin/bash",
        "arguments": arguments,
        "timeout": 1000
    }

    process_result = os.execute(parameters)

    # TODO: Inspect process result.

    return {
        "type": "success"
    }
