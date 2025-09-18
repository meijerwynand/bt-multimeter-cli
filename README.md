# Multimeter BLE CLI

A modular, config-driven Python command-line tool for connecting to, decoding, and exporting data from Bluetooth Low Energy (BLE) multimeters (e.g., ZOYI ZT-5B).

***

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Supported Devices](#supported-devices)
- [Installation](#installation)
- [Examples](#examples)
- [Usage](#usage)
- [Configuration](#configuration)
- [Extending Protocol Support](#extending-protocol-support)
- [Debugging](#debugging)
- [Collaboration & Contribution](#collaboration--contribution)
- [License](#license)

***

## Project Overview

This tool enables BLE scanning, deep GATT probing, and live decoding of multimeter data using a clean, testable, and config-first Python codebase. Designed for power-users, tinkerers, and developers seeking flexible integration or rapid reverse-engineering of new multimeter models.

***

## Features

- BLE device scan, connect, probe, and real-time decode
- Extensible protocol/config system for new device onboarding
- Flexible output to file, CSV, JSON, or streaming
- Debug display methods for developer insight and protocol tracing
- No web/frontend dependencies—CLI only

***

## Supported Devices

- ZOYI ZT-5B (others can be added via config and decoder extension)

***

## Installation

**Prerequisites:**  
- Python 3.8+  
- [bleak](https://github.com/hbldh/bleak) (`pip install bleak`)

**Clone and Install:**
```sh
git clone https://github.com/youruser/multimeter-cli.git
cd multimeter-cli
pip install -r requirements.txt
```

***

## Examples

**Scan for available BLE devices**
```sh
python cli/main.py --scan
```
_Output:_
```
Address: 9C:0C:35:03:C2:B7  |  Name: ZOYI-ZT5B
Address: 2F:3A:01:66:12:A4  |  Name: Multimeter-Test
-- END OF SCAN --
```

**Probe a BLE device (see model, manufacturer, full GATT layout)**
```sh
python cli/main.py --probe --device 9C:0C:35:03:C2:B7
```
_Output (truncated):_
```json
{
  "address": "9C:0C:35:03:C2:B7",
  "device_info": {
    "name": "ZOYI-ZT5B",
    "model": "ZT-5B",
    "manufacturer": "ZOYI"
  },
  "services": [
    {
      "uuid": "0000180a-0000-1000-8000-00805f9b34fb",
      "description": "Device Information",
      ...
    }
  ]
}
```
_Table output (truncated):_

```text
===== BLE Device Probe Summary =====
Address     : 9C:0C:35:03:C2:B7
Name        : None
Model       : BK-BLE-1.0
Manufacturer: BEKEN SAS

Services and Characteristics:
  Service: 00001801-0000-1000-8000-00805f9b34fb  (Generic Attribute Profile)
  Service: 0000fff0-0000-1000-8000-00805f9b34fb  (Vendor specific)
    - Char: 0000fff4-0000-1000-8000-00805f9b34fb   [read, write-without-response, notify] -- Vendor specific
 ...
  Service: 00001800-0000-1000-8000-00805f9b34fb  (Generic Access Profile)
    - Char: 00002a01-0000-1000-8000-00805f9b34fb   [read] -- Appearance  (val: 0000)
    - Char: 00002a00-0000-1000-8000-00805f9b34fb   [read] -- Device Name
=====================================

```

**Live decode with CSV output to terminal**
```sh
python cli/main.py --device 9C:0C:35:03:C2:B7 --config config/zt5b_minimal.json
```
_Output (CSV):_
```csv
timestamp,mode,value,unit
2025-09-18T17:00:01,Voltage,3.52,V
2025-09-18T17:00:02,Voltage,3.53,V
```

**Enable debug printing (edit your config file):**
```json
  "debug": {
    "device_info": true,
    "icons": true,
    "segments": false,
    "packet": false
  }
```
_(Will print additional diagnostic info as you run the CLI.)_

***

**Tip:**  
To use a different output file, add to your config:
```json
"output": {
  "destination": "file",
  "format": "csv",
  "fields": ["timestamp", "mode", "value", "unit"],
  "output_file": "today.csv",
  "newline_flush": true
}
```


***
## Usage

### Scan for Devices
```sh
python cli/main.py --scan
```

### Probe a Device (fetch model/manufacturer/services)
```sh
python cli/main.py --probe --device XX:XX:XX:XX:XX:XX
```

### Start Live Decoding
```sh
python cli/main.py --device XX:XX:XX:XX:XX:XX --config config/zt5b.json
```

***

## Configuration

All protocol and output settings are managed via JSON files in `config/`.  
See the included `zt5b.json` as a working reference.  
Key fields:
- BLE connection info (`char_uuid`, `xorkey`)
- Icon/segment regions and tables
- Output options (`destination`, `format`, `fields`)
- Debug toggles (verbose icon, segment, or packet output)

***

## Extending Protocol Support

To add a new multimeter model:
1. Use `--probe` to analyze GATT table and device info.
2. Create a new config JSON, mapping regions, icons, digits, and units as needed.
3. If a protocol is unique, subclass `DMMDecoder` and register it in the CLI.
4. Confirm correct output and mappings with debug options.

***

## Debugging

Enable debug fields in your config under `debug` to print device info, packet breakdown, or mapping tables for analysis.

***

## Collaboration & Contribution

- See `CONTRIBUTING.md` for code standards and onboarding tips.
- All contributions must include a session summary (context, decisions, next steps).
- Please discuss substantial changes or new model support before submitting PRs.

***

## License

MIT License.  
See [LICENSE](LICENSE) for details.

