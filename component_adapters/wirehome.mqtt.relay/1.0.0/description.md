# Summary
This adapter publishes a MQTT messages if the state is being changed. The used topic and payload for the states `on` and `off` can be modified.

# Configuration

Example:

```json
{
    "config": {
        "on": {
            "server": "192.168.1.10", // Optional broker address
            "topic": "bed/$patch/lamp-left",
            "payload": "on"
        },
        "off": {
            "server": "192.168.1.10", // Optional broker address
            "topic": "bed/$patch/lamp-left",
            "payload": "off"
        },
        "backward_channel": {
            "on": {
                "topic": "bed/$status/lamp-left",
                "payload": "on"
            },
            "off": {
                "topic": "bed/$status/lamp-left",
                "payload": "on"
            }
        }
    }
}
```