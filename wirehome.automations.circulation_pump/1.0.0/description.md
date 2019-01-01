# Summary
This automation controls a circulation pump for heating. It supports several types of modes like turning on if someone is present at the affected room or disabling it at a certain time to save energy.

# Configuration
The configuration of this automation contains the following JSON parameters.

* `duration`: Defines the duration (in seconds) which is required for the water to fully circulate
* `pause`: Defines the pause (in seconds) for every run. This is the time which is required by the water to cool down.
* `pump_uid`: The component UID of the pump which will be turned on and off.
* `triggers`: The list of motion detector or button UIDs which are triggering the circulation. The automation will select the proper event by checking the supported status.
* `disabled_range`: Defines the range (as start and end) where circulation is disabled completely even if triggers are fired.

```
{
    "config":
        {
            "duration": 180, // 3 minutes
            "pause": 3600, // 60 minutes
            "disabled_range": {
                "start": "23:00",
                "end": "07:00"
            },
            "pump_uid": "my_circulation_pump_1",
            "triggers": [
                "kitchen.motion_detector",
                "bathroom.motion_detector"
            ]
        }
}
```