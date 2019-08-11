# Summary
This automation applies the next available level of a fan when any of the configured buttons is pressed.
It is supported to set the level to 0 (off) when any of the buttons is pressed for a long time.

# Configuration

Example:

```json
{
    "buttons": [
        "button_1",
        "button_2",
        "button_3"
    ],
    "targets": [
        "fan_1",
        "fan_2",
        "fan_3"
    ]
}
```