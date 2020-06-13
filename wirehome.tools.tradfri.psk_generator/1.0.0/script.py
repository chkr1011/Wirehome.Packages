import json
import uuid


def main(parameters):
    # Mandatory parameters
    gateway_address = parameters.get("gateway_address", None)
    security_code = parameters.get("security_code", None)

    # Optional parameters
    identity = parameters.get("identity", str(uuid.uuid4()))

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

    response = __execute_coap_request__(
        gateway_address, "post", "15011/9063", payload, security_code)

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

    # Store new values. The gateway manager will pull values from here.
    wirehome.value_storage.write(
        "ikea/tradfri/gateway/address", gateway_address)
    wirehome.value_storage.write("ikea/tradfri/gateway/identity", identity)
    wirehome.value_storage.write("ikea/tradfri/gateway/psk", psk)

    return {
        "type": "success",
        "gateway_address": gateway_address,
        "identity": identity,
        "psk": psk,
        "version": version
    }


def __execute_coap_request__(gateway_address, method, uri, payload, security_code):
    request = {
        "client_uid": None,
        "host": gateway_address,
        "identity": "Client_identity",
        "key": security_code,
        "method": method,
        "path": uri,
        "payload": payload
    }

    response = wirehome.coap.request(request)
    # print(response)
    return response
