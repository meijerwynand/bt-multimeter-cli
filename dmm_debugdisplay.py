# dmm_debugdisplay.py

import json

class DMMDebugDisplay:
    """
    Developer/deep debug display utility.
    Accepts a dict of parsed or interpreted data, prints all fields in an informative way.
    Never mutates or enriches data—just displays.
    """

    def __init__(self, config=None):
        self.config = config or {}

    def show_packet(self, label, packet_dict):
        # Print a (labelled) JSON dump of the full data structure, with pretty formatting.
        print(f"[{label.upper()} DEBUG]")
        print(json.dumps(packet_dict, indent=2, ensure_ascii=False))

    def show_icon_debug(self, hexstring, parsed_result):
        # Focus on icon analysis
        print(f"[ICON DEBUG] hex={hexstring}")
        icons = parsed_result.get("icons", [])
        print(f"Active Icons: {icons}")
        print(json.dumps(parsed_result, indent=2, ensure_ascii=False))

    def show_segment_debug(self, hexstring, parsed_result):
        # Focus on segment/digit breakdown
        print(f"[SEGMENT DEBUG] hex={hexstring}")
        print(json.dumps(parsed_result, indent=2, ensure_ascii=False))

    def show_brief(self, parsed_result):
        # For when you only want to summarize a few key fields in a compact readout
        summary = {
            "value": parsed_result.get("value"),
            "mode": parsed_result.get("mode_label"),
            "unit": parsed_result.get("unit"),
            "icons": parsed_result.get("icons"),
        }
        print(f"[BRIEF] {summary}")
