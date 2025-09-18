# dmm_debugger.py

import json

class DMMDebugger:
    def __init__(self, debug_config, config):
        self.debug_icons = debug_config.get("icons", False)
        self.debug_segments = debug_config.get("segments", False)
        self.debug_device_info = debug_config.get("device_info", False)
        self.config = config

    def print_device_info(self):
        if self.debug_device_info:
            summary_keys = ["model", "name", "manufacturer", "chipset", "decoder", "char_uuid", "mode_map", "debug"]
            summary = {k: self.config.get(k) for k in summary_keys}
            print(json.dumps(summary, indent=2, ensure_ascii=False))


    def icon_debug(self, hexstring, decoder, result):
        icon_table = self.config["icon_table"]
        descriptions = self.config.get("descriptions", {})
        units = self.config.get("units", {})
        mode_map = self.config.get("mode_map", {})

        encoded_array = decoder.str2hexarray(hexstring)
        xorkey = decoder.xorkey
        if len(encoded_array) > len(xorkey):
            xorkey = (xorkey * ((len(encoded_array) // len(xorkey)) + 1))[:len(encoded_array)]
        xordecoded = decoder.bytewise_XOR(encoded_array, xorkey)
        binary = decoder.hex2bin(xordecoded)
        flipped = decoder.flip_bits(binary)
        bitstring = decoder.array2str(flipped)
        icon_bits = decoder.extract_icon_bits(bitstring)

        active_indices = [i for i, b in enumerate(icon_bits) if b == '1' and i < len(icon_table)]
        active_icons = [icon_table[i] for i in active_indices]
        index_icon_table = {str(i): icon_table[i] for i in active_indices}

        mode_label = self.detect_most_overlap_mode_label(
            active_icons, self.config["mode_label_map"]
        )
        description, unit = self.compose_description_and_unit(
            active_indices, icon_table, descriptions, units
        )

        debug_block = {
            "hexstring": hexstring,
            "decoded_bytes": xordecoded,
            "full_bitstring": bitstring,
            "icon_region_bitmask": icon_bits,
            "active_indices": active_indices,
            "active_icons": active_icons,
            "index_icon_table": index_icon_table,
            "mode_label": mode_label,
            "description": description,
            "unit": unit,
            "final_result": result
        }
        print("[ICON DEBUG]\n" + json.dumps(debug_block, ensure_ascii=False, indent=2))

    def segment_debug(self, hexstring, decoder, result):
        debug_block = {
            "hexstring": hexstring,
            "decoded_bytes": result.get("decoded_bytes", []),
            "value": result.get("value", None),
            "raw_segments": result.get("raw_segments", None),
            "final_result": result
        }
        print("[SEGMENT DEBUG]\n" + json.dumps(debug_block, ensure_ascii=False, indent=2))

    def compose_description_and_unit(self, active_indices, icon_table, descriptions, units):
        icon_keys = [icon_table[i] for i in active_indices]
        description = ' '.join([descriptions.get(key, key) for key in icon_keys if descriptions.get(key, key)])
        unit = ''.join([units.get(key, '') for key in icon_keys])
        return description.strip(), unit.strip()

    def detect_most_overlap_mode_label(self, active_icons, mode_label_map):
        best_label = "unknown"
        max_overlap = 0
        for label, icons in mode_label_map.items():
            overlap = len(set(icons) & set(active_icons))
            if overlap > max_overlap:
                best_label = label
                max_overlap = overlap
        return best_label

    def print_digit_windows(self, segment_bits, digit_table):
        for i in range(len(segment_bits)-6):
            window = segment_bits[i:i+7]
            print(f'Offset {i}: {window} = {digit_table.get(window, " ")}')
