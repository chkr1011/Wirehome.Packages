import json


def main(parameters):
    gateway_address = parameters.get("gateway_address", None)
    security_code = parameters.get("security_code", None)
    identity = parameters.get("identity", "wirehome")

    if gateway_address == None:
        return {
            "type": "exception.parameter_invalid",
            "parameter_name": "gateway_address"
        }

    if security_code == None:
        return {
            "type": "exception.parameter_invalid",
            "parameter_name": "security_code"
        }

    payload = '{{"9090":"{identity}"}}'.format(identity=identity)

    process_result = __execute_coap_request__(gateway_address, "post", "15011/9063", payload, "Client_identity", security_code)
    if process_result.get("type", None) != "success" or process_result.get("exit_code", None) != 0:
        return process_result

    gateway_result = process_result["output_data"]
    if gateway_result == "":
        return {
            "type": "exception",
            "message": "The specified identity is already used. Please use a new one."
        }

    result = json.loads(gateway_result)

    psk = result.get("9091", None)
    version = result.get("9029", None)

    if psk == None or version == None:
        return process_result

    return {
        "type": "success",
        "identity": identity,
        "psk": psk,
        "version": version
    }


def __execute_coap_request__(address, method, uri, payload, identity, psk):
    uri = "coaps://{a}:5684/{u}".format(a=address, u=uri)

    escapedPayload = payload.replace('"', '""')
    arguments = '-c "coap-client -m {} -u "{}" -k "{}" -e \'{}\' "{}""'.format(
        method,
        identity,
        psk,
        escapedPayload,
        uri)

    parameters = {
        "file_name": "/bin/bash",
        "arguments": arguments,
        "timeout": 1000
    }

    execute_result = wirehome.os.execute(parameters)
    execute_result["arguments"] = arguments

    return execute_result
