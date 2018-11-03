# Summary 
This automation opens and closes roller shutters depending on outdoor sunrise, sunset and temperature.

# Configuration
```json
{
    "config":{
        "roller_shutters": ["rs1", "rs2"]
    }
}
```

# Settings
```json
{
    "open_on_sunrise": true,
    "close_on_sunset": true,
    "sunrise_shift": "-00:30:00",
    "sunset_shift": "00:30:00",
    "disabled_before": "07:45",
    "min_outdoor_temperature": 2,
    "auto_close_outdoor_temperature": 25
}
```