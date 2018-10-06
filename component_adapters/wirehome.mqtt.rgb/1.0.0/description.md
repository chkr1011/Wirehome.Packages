# Summary
This adapter publishes a MQTT messages if the state (power, brightness, color) is being changed. The used topic and payload template can be specified.

# Configuration
Example:
```json
{
    "config": {
        "max_pwm_value": 1023, // Defines the value for PWM when value is set to 100 %.
        "set_color_message": {
            "topic": "bed/$patch/rgb",
            "payload_template": "{r};{g};{b}" // Also a JSON document may be used here.
        },
        "turn_off_message": { // Some devices are having a dedicated relay which turns the strip off completely. When not defined "0;0;0" is sent by default.
            "topic": "bed/$patch/rgb",
            "payload": "0;0;0"
        }
    }
}
```