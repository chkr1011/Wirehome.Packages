# Heating Service

## Summary

This service controls all heating devices in the installation.

## Configuration

```json
{
    "config":
    {
        "monitoring_settings":
        {
            "interval": 120
        },
        "zones":
        {
            "office":
            {
                "temperature_sensors":
                {
                    "office.temperature_sensor": {}
                },
                "windows": 
                {

                }
            }
        }
    }
}
```
