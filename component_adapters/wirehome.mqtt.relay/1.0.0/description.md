# Summary

This adapter publishes a MQTT messages if the state is being changed. The used topic and payload for the states `on` and `off` can be modified.

# Configuration

Example:

```json
{
    "config": {
        "on": {
            "topic": "bed/$patch/lamp-left",
            "payload": "on"
        },
        "off": {
            "topic": "bed/$patch/lamp-left",
            "payload": "off"
        }
    }
}
```