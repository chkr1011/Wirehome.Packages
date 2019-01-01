# Summary
This component adapter wraps a _Tasmota_ relay device like a _Sonoff Pow_.

# Prerequisites
The _Tasmota_ device must be up and running and connected to the integrated Wirehome.Core MQTT broker.

# Logic compatibility
This adapter is compatible with the following component logics.

1. wirehome.lamp
2. wirehome.socket

# Configuration
If the default values in _Tasmota_ are not changed the required configuration value is the used topic only.

```json5
{
    "config": {
        "topic": "socket-1" // The topic from the Tasmota settings.
    }
}
```