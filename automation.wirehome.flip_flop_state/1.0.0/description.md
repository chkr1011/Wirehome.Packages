# Summary

This automation applies a defined state for a state machine when a button is pressed or motion is detected. If the state is already applied a second defined state is applied.

# Configuration

Example:

```json
{
    "config": {
        "flip_state": "on",
        "flop_state": "off",
        "buttons": {
            "button1": {
                "event": "pressed"
            }   
        },
        "targets": [
            "lamp1"
        ]
    }
}
```