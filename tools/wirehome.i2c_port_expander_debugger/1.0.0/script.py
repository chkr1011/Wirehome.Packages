def main(parameters):
    ic = parameters.get("ic", "PCF8574")
    bus_id = parameters.get("bus_id", "")
    address = parameters["address"]
    operation = parameters.get("operation", "read")

    registers = []

    if ic == "PCF8574" or ic == "PCF8574A":
        state = list(i2c.read(bus_id, address, 1))

        registers.append({
            "state_array": state,
            "state_ulong": convert.list_to_ulong(state),
            "state_hex": convert.list_to_hex_string(state),
            "state_bits": convert.list_to_bit_string(state),
        })

    elif ic == "MAX7311" or ic == "PCA9555":
        write_buffer = [0]
        state = list(i2c.write_read(bus_id, address, write_buffer, 9))

        offset = 0
        for register in state:
            registers.append({
                "offset": offset,
                "state_byte": register,
                "state_hex": convert.list_to_hex_string([register]),
                "state_bits": convert.list_to_bit_string([register]),
            })

            offset += 1

    return {
        "type": "success",
        "registers":  registers
    }
