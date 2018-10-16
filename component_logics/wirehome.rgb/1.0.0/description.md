# Summary
This logic is a simple RGB lamp which supports a RGB color.

# Configuration

Example:
```json
{
    "config": {
        "default_color": {
            "red": 255,
            "green": 255,
            "blue": 255
        },
        "available_colors": {
            "white": {
                "red": 255,
                "green": 255,
                "blue": 255
            },
            "blue": {
                "red": 0,
                "green": 0,
                "blue": 255
            },
            "red": {
                "red": 255,
                "green": 0,
                "blue": 0
            },
            "green": {
                "red": 255,
                "green": 0,
                "blue": 0
            }
        }
    }
}
```