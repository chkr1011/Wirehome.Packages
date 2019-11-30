# Summary

This adapters maps several MQTT topics of a sensor and pushes them to the component logic. The value of the sensor is read from the payload. The value of the payload will be converted to a string in all cases.
Each individual value from an MQTT topic is mapped via a custom key.

## Configuration

Example:

```json
{
    "config": {
        "key1": {
            "topic": "mySensorTopic/0"
        },
        "key2": {
            "topic": "mySensorTopic/1"
        }
    }
}
```