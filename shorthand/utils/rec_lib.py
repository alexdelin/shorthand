
def get_hex_int(hex_string):
    '''Parse a hexadecimal string and return
    the parsed value as an integer
    '''

    is_negative = False
    unsigned_hex_string = hex_string

    if hex_string[0] == '-':
        is_negative = True
        unsigned_hex_string = hex_string[1:]
    if len(unsigned_hex_string) < 3:
        raise ValueError('Invalid_hex_string')
    int_value = int(unsigned_hex_string[2:], 16)
    if is_negative:
        int_value = int_value * -1
    return int_value
