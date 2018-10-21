# Summary

This service injects a static value for the status `power.consumption` depending on the current status of a component. The service attached itself to all status changes of all components and updates the status depending on the current status.

# Configuration

The service requires a status description and the UID of the affected component.

```json

{
    "values": {
        "my_component_1": {
            "default_value": 0,
            "set_to_default_when_off": true,
            "power_consumptions": [
                {
                    "value": 15,
                    "pattern": [
                        {
                            "status": "power.state",
                            "operator": "==",
                            "value": "on"
                        }
                    ]
                }
            ]
        }
    }
}

```