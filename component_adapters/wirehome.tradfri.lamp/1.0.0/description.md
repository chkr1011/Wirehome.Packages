# Summary 
This adapter wraps a lamp from IKEA called Tradfri. In order to use this adapter some requirements must be met.
1. An IKEA gateway must be available.
2. The lamp must be already paired with the gateway.
3. The firmware of the gateway must be up to date.
4. The hostname (e.g. GW-B8E6AF2C2FA4) or IP of the gateway must be known.
5. The security code from the gateway must be known (written on the back).
6. The user defined name of the device must be known.
7. The tool `coap-client` must be installed on the hosting machine.
8. The PSK for accessing the gateway must be generated first using the Wirehome Tool `wirehome.tradfri.psk_generator`.

## Installation instructions for `coap-client`
Please follow the instructions described here:

https://github.com/ggravlingen/pytradfri/blob/master/script/install-coap-client.sh

# Configuration

Example:

```json
{
    "config":
    {
        "gateway_address": "GW-B8E6AF2C2FA4",
        "psk": "1234567890abcdefgh",
        "device_id": 65550, // Either use ID or name (ID requires no lookup)
        "device_name": "TV rechts", // Either use ID or name (Name requires a lookup)
    }
}
```