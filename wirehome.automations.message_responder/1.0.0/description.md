# Message Responder

## Summary

This automation can send new messages based on received ones. For example subscribing a button trigger message and sending a light command when the input message was received.

## Example

```json
"config":
{
    "observations": {
        "motion_detecor_bedroom_deactivation": {
            "input_messages": {
                "button_floor_pressed": {
                    "filter":{
                        "type": "wirehome.button.event.triggered",
                        "component_uid": "floor_upper.button"
                    }
                },
                "button_bed_right_triggered": {
                    "filter":{
                        "type": "wirehome.button.event.triggered",
                        "component_uid": "bedroom.button.bed_right_right"
                    }
                },
                "button_bed_left_triggered": {
                    "filter":{
                        "type": "wirehome.button.event.triggered",
                        "component_uid": "bedroom.button.bed_left_left"
                    }
                }
            },
            "component_messages": {
                "disable_motion_detector": {
                    "component_uid": "bedroom.motion_detector",
                    "message": {
                        "type": "disable"
                    }
                }
            }
        }
    }
}
```
