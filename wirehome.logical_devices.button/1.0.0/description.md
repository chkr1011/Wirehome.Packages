# Summary
This logic is a button which supports the following features:

* Reflecting the pressed state (`pressed`, `released`).
* Sending a `triggered` event if the button is pressed shortly (pressed and released) or hold for a specified time.

## Custom event definitions
### Triggered
Each button will generate a `triggered` event after it is released or a certain amount of time elapsed (see config).

Event properties:
* `type`: The type is always set to _wirehome.button.event.triggered_.
* `duration`: The value is either `short` or `long`.
* `component_uid`: The UID of the affected component.

Example:
```json
{
    "type": "wirehome.button.event.triggered",
    "duration": "short",
    "component_uid": "office.button.door_bottom_right"
}
```

# Configuration
The configuration of this automation contains the following JSON parameters.

* `long_press_max_duration`: Defines the duration (in milliseconds) which is used to identify a held button before generating the `triggered` event.

```json
{
    "config": {
        "long_press_max_duration": 2500
    }
}
```