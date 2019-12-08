# Heating Service

## Summary

This service controls all heating devices in the installation. It monitors the windows and temperature sensors in a zone and updates the valves according to the current settings etc.
Features:

1. Create unlimited zones (must not match component groups).
2. Create reductions which use a different target temperature (night reduction etc.).
3. Monitor windows and stop heating in case of an opened window.
4. Monitor several temperature sensors per zone and update valves accordingly.

## Configuration

```json
{
    "config":
    {
        "monitoring":
        {
            "interval": 5000,
            "temperature_delta": 3,
        },
        "outdoor":
        {
            "temperature_sensor": "garden"
        },
        "reductions": {
            "night": {
                "begin": "23:00:00",
                "end": "06:00:00",
                "target_temperature": 16
            }
        },
        "zones":
        {
            "office":
            {
                "is_enabled": true,
                "target_temperature": 22,
                "temperature_sensors":
                {
                    "office.sensor.temperature": {}
                },
                "windows":
                {
                    "office.window.left_l": {},
                    "office.window.left_r": {},
                    "office.window.right_l": {},
                    "office.window.right_r": {},
                },
                "valves": {
                    "heating.valve.office": {}
                },
                "reductions": {
                    "night-special": {
                        "begin": "01:00:00",
                        "end": "04:00:00",
                        "target_temperature": 10
                    }
                }
            }
        }
    }
}
```
