# Summary
This automation starts a fan in level 1 when motion is detected. After time `first_level_duration` the speed of the fan will be set to level 2 for the time of `second_level_duration`. 

The level will stay at 1 as long as motion is detected.

# Configuration
Example:

```json
{
    "config": {
        "motion_detectors": ["myDetector1"],
        "fans": ["myFan1"],
        "first_level_duration": 480000, // 8 mins in ms
        "second_level_duration": 720000 // 12 mins in ms
    }
}
```