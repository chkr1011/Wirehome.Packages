# Window Monitor

## Summary

This service monitors all configured windows and shows notifications when any of the windows is open etc. The service also contains a panel which shows the status summary of all tracked windows.

## Configuration

```json
{
    "config":
    {
        "monitoring_settings":
        {
            "interval": 120
        },
        "notification_settings":
        {
            "send_notifications": true,
            "notification_level": "warning",
            "window_open_duration_threshold": 600
        },
        "tracked_windows":
        {
            "window1":
            {
                
            },
            "window2":
            {

            }
        }
    }
}
```
