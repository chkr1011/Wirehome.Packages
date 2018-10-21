# Summary

This tool allows reading and writing the registers of I2C port expanders.
The following port expanders are supported.
* PCF8574
* PCF8574A
* MAX7311
* PCA9555

# Parameters

## Reading
When executed the tool accepts the following set of parameters to performa a read operation:

```json
{
    "bus_id": "", // optional
    "address": 56,
    "ic": "PCF8574", // default
    "operation": "read"
}
```

The result of the reading process is returned in the following format:

```json
{
    "type": "success",
    "registers": [
        {
            "offset": 0, // Index of the register
            "state_byte": 255,
            "state_hex": "FF",
            "state_bits": "11111111"
        },
        {
            "offset": 1, // Index of the register
            "state_byte": 0,
            "state_hex": "00",
            "state_bits": "00000000"
        }
    ]
}
```