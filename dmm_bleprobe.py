# dmm_bleprobe.py

from bleak import BleakClient, BleakScanner

DEVICE_INFO_SERVICE = "0000180a-0000-1000-8000-00805f9b34fb"
CHAR_UUIDS = {
    "model": "00002a24-0000-1000-8000-00805f9b34fb",
    "manufacturer": "00002a29-0000-1000-8000-00805f9b34fb",
}

class DMMBLEProbe:
    async def scan_devices(self, timeout=5):
        devices = await BleakScanner.discover(timeout=timeout)
        return [{"address": d.address, "name": d.name} for d in devices]

    async def probe_device(self, address):
        result = {"address": address, "device_info": {}, "services": []}
        async with BleakClient(address) as client:
            # Try device name (from advertisement)
            result["device_info"]["name"] = getattr(client, "device", None).name if hasattr(client, "device") else None

            # Try Device Information Service
            for k, uuid in CHAR_UUIDS.items():
                try:
                    val = await client.read_gatt_char(uuid)
                    result["device_info"][k] = val.decode(errors="replace")
                except Exception:
                    result["device_info"][k] = None

            # Enumerate all services/chars (NO ()/await, just property)
            services = client.services
            for service in services:
                chars = []
                for char in service.characteristics:
                    char_info = {
                        "uuid": char.uuid,
                        "properties": char.properties,
                        "description": char.description,
                    }
                    # Optionally, try to read value if readable
                    if "read" in char.properties:
                        try:
                            cval = await client.read_gatt_char(char.uuid)
                            char_info["value"] = cval.hex()
                        except Exception:
                            char_info["value"] = None
                    chars.append(char_info)
                result["services"].append({
                    "uuid": service.uuid,
                    "description": service.description,
                    "characteristics": chars,
                })
        return result


    @staticmethod
    def print_device_summary(probe_result):
        print("\n===== BLE Device Probe Summary =====")
        info = probe_result.get("device_info", {})
        print(f"Address     : {probe_result.get('address', '-')}")
        print(f"Name        : {info.get('name', '-')}")
        print(f"Model       : {info.get('model', '-')}")
        print(f"Manufacturer: {info.get('manufacturer', '-')}\n")
        print("Services and Characteristics:")
        for svc in probe_result.get("services", []):
            desc = svc.get('description', 'Unknown')
            print(f"  Service: {svc['uuid']}  ({desc})")
            for char in svc.get('characteristics', []):
                cdesc = char.get('description', 'Unknown')
                props = ", ".join(char.get('properties', []))
                val = char.get('value', '')
                print(f"    - Char: {char['uuid']:<38} [{props}] -- {cdesc}" + (f"  (val: {val})" if val else ""))
        print("=====================================\n")