# Summary
This automation starts a fan in level 1 when motion is detected. After time `first_level_duration` the speed of the fan will be set to 0.

The level will stay at 1 as long as motion is detected.

# Configuration
Example:

```json
{
    "config": {
        "motion_detectors": ["myDetector1"],
        "fans": ["myFan1"],
        "duration": 480000, // 8 mins in ms
        "target_level": 1 // The level which should be applied (default = 1)
    }
}
```