# main.py

import argparse
import asyncio
import json
from datetime import datetime
from bleak import BleakClient, BleakScanner

from dmm_decoder import ZT5BDecoder
from dmm_interpreter import DMMInterpreter
from dmm_debugdisplay import DMMDebugDisplay
from output_handler import OutputHandler
from dmm_bleprobe import DMMBLEProbe

def parse_args():
    parser = argparse.ArgumentParser(description="DMM BLE CLI Tool")
    parser.add_argument('--scan', action='store_true', help='Scan for BLE devices')
    parser.add_argument('--probe', action='store_true', help='Probe device for GATT and info')
    parser.add_argument('--device', type=str, help='Bluetooth MAC address of device to connect')
    parser.add_argument('--config', type=str, default="../config/zt5b_minimal.json", help='Path to config JSON')
    return parser.parse_args()


async def perform_scan():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover(timeout=5)
    for d in devices:
        print(f"Address: {d.address}  |  Name: {d.name}")
    print("-- END OF SCAN --")

def load_config(path):
    with open(path, "r") as f:
        return json.load(f)

def select_decoder(config):
    if config.get("decoder") == "ZT5BDecoder":
        return ZT5BDecoder(config)
    raise ValueError(f"Unknown decoder specified: {config.get('decoder')}")

def notification_handler_factory(decoder, interpreter, display, outputter, debug_config):
    def notif_handler(sender, data):
        try:
            hexstr = data.hex().lower()
            raw_result = decoder.decode_packet(hexstr)
            result = interpreter.interpret(raw_result)

            if debug_config.get("packet", False):
                display.show_packet("packet", result)
            if debug_config.get("icons", False):
                display.show_icon_debug(hexstr, result)
            if debug_config.get("segments", False):
                display.show_segment_debug(hexstr, result)

            output_payload = {
                "timestamp": datetime.now().isoformat(),
                "mode": result.get("mode_label", ""),
                "value": result.get("value", ""),
                "unit": result.get("unit", ""),
            }
            outputter.write(output_payload)
        except Exception as e:
            print(f"[NOTIF HANDLER ERROR] {type(e).__name__}: {e}")

    return notif_handler

async def main():
    args = parse_args()
    if args.scan:
        results = await DMMBLEProbe().scan_devices()
        for d in results:
            print(f"Address: {d['address']} | Name: {d['name']}")
        return

    if args.probe and not args.device:
        print("Error: --device argument required with --probe.")
        return

    if args.probe:
        if not args.device:
            print("Error: --device argument required with --probe.")
            return
        probe = DMMBLEProbe()
        probe_result = await probe.probe_device(args.device)
        print(json.dumps(probe_result, indent=2, ensure_ascii=False))
        probe.print_device_summary(probe_result)    # <-- Class method call
        return

    if not args.device:
        print("Error: --device argument required unless scanning (--scan).")
        return

    config = load_config(args.config)
    outputter = OutputHandler(config["output"])
    decoder = select_decoder(config)
    interpreter = DMMInterpreter(config)
    display = DMMDebugDisplay(config)
    char_uuid = config.get("char_uuid")
    debug_config = config.get("debug", {})

    if debug_config.get("device_info", False):
        try:
            print(json.dumps({
                k: config.get(k)
                for k in [
                    "model", "name", "manufacturer", "chipset", 
                    "decoder", "char_uuid", "mode_map", "debug"
                ]
            }, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"[CONFIG INFO ERROR] {type(e).__name__}: {e}")

    async with BleakClient(args.device) as client:
        await client.start_notify(
            char_uuid,
            notification_handler_factory(decoder, interpreter, display, outputter, debug_config)
        )
        print("\nListening for BLE notifications. Ctrl+C to exit.")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            await client.stop_notify(char_uuid)
            print("Stopped.")

if __name__ == "__main__":
    asyncio.run(main())
