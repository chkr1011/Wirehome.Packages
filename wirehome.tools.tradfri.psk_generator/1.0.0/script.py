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

    response = __execute_coap_request__(gateway_address, "post", "15011/9063", payload, security_code)

    if response.get("type", None) != "success":
        return response

    gateway_result = response["payload"]
    if gateway_result == "":
        return {
            "type": "exception",
            "message": "The specified identity is already used. Please use a new one."
        }

    result = json.loads(gateway_result)

    psk = result.get("9091", None)
    version = result.get("9029", None)

    if psk == None or version == None:
        return response

    return {
        "type": "success",
        "identity": identity,
        "psk": psk,
        "version": version
    }


def __execute_coap_request__(method, uri, payload, security_code):
    address = config.get("gateway_address", None)
    identity = config.get("identity", "wirehome")
    psk = config.get("psk", None)

    request = {
        "client_uid": "tradfri_gateway_manager",
        "host": address,
        "identity": "Client_identity",
        "key": security_code,
        "method": method,
        "path": uri,
        "payload": payload
    }

    response = wirehome.coap.request(request)
    # print(response)
    return response
