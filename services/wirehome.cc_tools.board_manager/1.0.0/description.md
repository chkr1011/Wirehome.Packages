# Summary

This service is a abstraction layer for IO boards from _CCTools_. It allows changing the pins individually without the need of sending the whole device state. The pull device state is managed in this service.

# Supported boards

The following boards are supported.

* `HSRel 5+3`
* `HSRel 8+8`
* `HSPE 8`
* `HSPE 16`

# Parameters

The following example shows a configuration with several parameters.

```json
{
    "config": {
        "testHSREL5": {
            "board": "HSREL5",
            "bus_id": "", // optional
            "address": 32
        },
        "testHSREL5_2": {
            "board": "HSREL5",
            "bus_id": "", // optional
            "address": 33
        },
        "input-0": {
            "board": "HSPE16-IN",
            "bus_id": "", // optional
            "address": 46,
            "interrupt_gpio_id": 5,
            "interrupt_gpio_host_id": "", // optional
            "fetch_mode": "poll_interrupt"
        }
    }
}
```