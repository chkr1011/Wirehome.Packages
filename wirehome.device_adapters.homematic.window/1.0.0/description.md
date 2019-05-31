# Summary
This adapter wraps a generic Homematic device and watches a property as the sensor value.
It requires a configured Homematic CCU and the wirehome.services.homematic.ccu service to be installed.

# Configuration

Example:

```json
{
    "config":
    {
        // the address of the window contact from the CCU webinterface
        "address": "0012888395C123:1",

        // optional, the name of the property that should be watched.
        // defaults to STATE, overwriting to WINDOW_STATE allows to watch
        // a contact that is linked directly to a thermostat.
        "property": "STATE"
    }
}
```