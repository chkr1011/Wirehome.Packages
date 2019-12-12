# Summary

This logic is a simple sensor which supports numeric values. The value of the sensor can be published as a global variable automatically.

Supported sensor types

1. Temperature (°C)
2. Humidity (%)
3. Pressure (hPa)

# Configuration

```json
{
    "config": {
        "sensor_type": "temperature", // "temperature" | "humidity" | "pressure"
        "publish_as_global_variable": "xyz", // optional
        "outdated_timeout": 60000 // Defines the time when the sensor is outdated when no update is received.
    }
}
```