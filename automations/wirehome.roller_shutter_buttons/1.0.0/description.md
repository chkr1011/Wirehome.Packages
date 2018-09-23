# Summary

This automation accepts two regular buttons and uses them to move and stop a roller shutter. The default behavior is:
* Move up when "up" is pressed
* Move down when "down" is pressed
* Stop when target state is already matching ("up" + "up" > "stop")

# Configuration

Example:

```json
{
    "config": {
        "up_button": "children_1.button.up",
        "down_button": "children_1.button.down",
        "roller_shutter": "children_1.roller_shutter"
    }
}
```