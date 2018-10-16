# Summary
This adapters maps a MQTT topic to a sensor value and pushes it to the component logic. The value of the sensor is read from the payload. The value of the payload will be converted to a string in all cases.

# Configuration

Example:

```json
{
    "config": {
        "topic": "mySensorTopic/0"
    }
}
```