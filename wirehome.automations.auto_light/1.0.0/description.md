# Summary 
This automation turns on a component when motion is detected. It also turns it of after the time of `duration` when motion is no longer detected.

# Configuration
```json5
{
    "config":{
        "motion_detectors": ["myDetector1"],
        "targets": ["myLamp1", "myLamp2"],
        "duration": 5000 // 5 secs in ms
    }
}
```