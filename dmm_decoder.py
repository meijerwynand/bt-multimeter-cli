# dmm_decoder.py

import json

class DMMDecoder:
    """Base class for DMM screen/binary decoders."""
    def __init__(self, config):
        self.xorkey = self.str2hexarray(config["xorkey"])
        self.icon_table = config["icon_table"]
        self.digit_table = config.get("digit_table", {})  # Load digit table from config

        self.regions = config["regions"]     

    @staticmethod
    def str2hexarray(string):
        string = string.replace(' ', '').lower()
        return [int(string[i:i+2], 16) for i in range(0, len(string), 2)]

    @staticmethod
    def bytewise_XOR(array, xorkey):
        return [array[x] ^ xorkey[x % len(xorkey)] for x in range(len(array))]

    @staticmethod
    def hex2bin(array):
        return [bin(x)[2:].zfill(8) for x in array]

    @staticmethod
    def flip_bits(array):
        return [b[::-1] for b in array]

    @staticmethod
    def array2str(array):
        return ''.join(array)

    def extract_icon_bits(self, bitstring):
        bits = self.regions["icon"]
        # Two ranges—concatenate if length 4
        if len(bits) == 4:
            return bitstring[bits[0]:bits[1]] + bitstring[bits[2]:bits[3]]
        elif len(bits) == 2:
            return bitstring[bits[0]:bits[1]]
        else:
            raise ValueError("icon region must have 2 or 4 values")


    def extract_segment_bits(self, bitstring):
        bits = self.regions["segment"]
        return bitstring[bits[0]:bits[1]]


    def decode_icons(self, icon_bits):
        return [self.icon_table[i] for i, b in enumerate(icon_bits) if b == '1' and i < len(self.icon_table)]

    def display_decoder(self, segment_bits):
        digit_table = self.digit_table
        # Split into 8-bit groups (adjust slice as needed)
        groups = [segment_bits[i:i+8] for i in range(0, len(segment_bits), 8)]
        number = ""
        for idx, group in enumerate(groups):
            if len(group) < 8:
                continue  # Skip incomplete group
            if idx == 0 and group[0] == "1":
                number += "-"
            if idx > 0 and group[0] == "1":
                number += "."
            val = digit_table.get(group[1:], " ")
            number += str(val)
        try:
            return float(number)
        except Exception:
            return number

    def decode_packet(self, hexstring):
        encoded_array = self.str2hexarray(hexstring)
        # pad xorkey if needed
        xorkey = (self.xorkey * ((len(encoded_array) // len(self.xorkey)) + 1))[:len(encoded_array)]
        xordecoded = self.bytewise_XOR(encoded_array, xorkey)
        binary = self.hex2bin(xordecoded)
        flipped = self.flip_bits(binary)
        bitstring = self.array2str(flipped)
        icon_bits = self.extract_icon_bits(bitstring)
        icons = self.decode_icons(icon_bits)
        # --- SEGMENT VALUE EXTRACTION ---
        segment_bits = self.extract_segment_bits(bitstring)
        value = self.display_decoder(segment_bits) if segment_bits else None
        result = {
            'icons': icons,
            'decoded_bytes': xordecoded,
            'value': value,
            'raw_segments': segment_bits
        }
        return result

# Example derived decoder for ZT-5B
class ZT5BDecoder(DMMDecoder):
    def __init__(self, config):
        super().__init__(config)
        # ZT-5B-specific setup if needed

# --- Usage Example ---
if __name__ == "__main__":
    # Minimal config example
    config = {
        "xorkey": "41217355a2c1327166aa3bd0e2a833142021aabb",
        "icon_regions": {
            "default": [24, 28, 60, 87]
        },
        "icon_table": [
            "LowBattery","Delta","BT","BUZ","HOLD","ºF","ºC","DIODE",
            "MAX","MIN","%","AC","F","u(F)","m(F)","n(F)","Hz",
            "ohm","K(ohm)","M(ohm)","V","m(V)","DC","A","AUTO",
            "?7","u(A)","m(A)","?8","?9","?10","?11"
        ],
        # Add your digit_table in config!
        "digit_table": {
            "1111101": 0, "0000101": 1, "1011011": 2, "0011111": 3,
            "0100111": 4, "0111110": 5, "1111110": 6, "0010101": 7,
            "1111111": 8, "0111111": 9, "1110111": "A", "1001100": "u",
            "1101010": "t", "1001110": "o", "1101000": "L", "1111010": "E",
            "1110010": "F", "0000000": " ", "0000010": "-"
        }
    }

    decoder = ZT5BDecoder(config)
    hexstring = "1b847195453ad9fa668a"
    result = decoder.decode_packet(hexstring)
    print(json.dumps(result, ensure_ascii=False, indent=2))
