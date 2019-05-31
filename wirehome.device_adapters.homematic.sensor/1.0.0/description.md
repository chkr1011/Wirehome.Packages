# Summary
This adapter wraps a generic Homematic device and watches a property as the sensor value.
It requires a configured Homematic CCU and the wirehome.services.homematic.ccu service to be installed.

# Configuration

Example:

```json
{
    "config":
    {
        "address": "0012888395C123:1",  // the address of the device from the CCU webinterface
        "property": "ACTUAL_TEMPERATURE"  // the name of the property that should be watched
    }
}
```