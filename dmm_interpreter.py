# dmm_interpreter.py

class DMMInterpreter:
    """
    Interprets raw decoder dicts: assigns mode label, unit, human conversions, error states, etc.
    Stateless, pure enrichment only. Output is a new, enriched dict.
    """
    def __init__(self, config):
        self.icon_table = config.get("icon_table", [])
        self.mode_label_map = config.get("mode_label_map", {})
        self.units = config.get("units", {})
        self.descriptions = config.get("descriptions", {})

    def interpret(self, raw_result):
        # Work with a copy, never mutate input
        result = raw_result.copy()
        active_icons = result.get("icons", [])
        # Mode detection
        mode_label = self.detect_most_overlap_mode_label(active_icons)
        # Description (optional: combine icon descriptions for human label)
        description = self.compose_description(active_icons)
        # Unit field
        unit = self.compose_unit(active_icons)
        # Attach enriched fields
        result["mode_label"] = mode_label
        result["description"] = description
        result["unit"] = unit
        # Optionally add more: e.g., error/state field normalization
        return result

    def detect_most_overlap_mode_label(self, active_icons):
        best_label = "unknown"
        max_overlap = 0
        for label, icons in self.mode_label_map.items():
            overlap = len(set(icons) & set(active_icons))
            if overlap > max_overlap:
                best_label = label
                max_overlap = overlap
        return best_label

    def compose_description(self, active_icons):
        # Optional: human-friendly mode description (icons to words)
        return " ".join([self.descriptions.get(icon, icon) for icon in active_icons if self.descriptions.get(icon)])

    def compose_unit(self, active_icons):
        # Concatenate units for all found icons (if any)
        return "".join([self.units.get(icon, "") for icon in active_icons])
