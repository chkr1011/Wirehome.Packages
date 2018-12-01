# Summary
This component adapter wraps a _Tasmota_ RGB device like a _MagicHome LED strip controller_.

# Prerequisites
The _Tasmota_ device must be up and running and connected to the integrated Wirehome.Core MQTT broker.

# Logic compatibility
This adapter is compatible with the following component logics.

1. wirehome.lamp

# Configuration
If the default values in _Tasmota_ are not changed the required configuration value is the used topic only.

```json5
{
    "config": {
        "topic": "office-rgb" // The topic from the Tasmota settings.
    }
}
```