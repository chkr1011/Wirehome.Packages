# Summary
This logic is a roller shutter which supports the following features:

* Moving up, down and stop
* Track position via time it's moving
* Automatically turn off to save energy (relays etc.)
* Publish power consumption via using a static value when moving

# Configuration
```json
{
    "config": {
        "static_power_consumption": 30, // in watts / h
        "max_position": 20000, // duration in ms (the duration which is required to close completely)
        "auto_off_timeout": 30000 // duration in ms (the duration when the roller shutter is turned off after moving started)
    }
}
```