# output_handler.py

import sys
import json
import csv
# import asyncio/websockets if/when adding websocket output

class OutputHandler:
    def __init__(self, output_config):
        self.destination = output_config["destination"]
        self.format = output_config["format"]
        self.fields = output_config.get("fields", ["timestamp", "mode", "value", "unit", "icons"])
        self.newline_flush = output_config.get("newline_flush", False)
        self.output_file = output_config.get("output_file")
        self.websocket_url = output_config.get("websocket_url")
        self._validate_config()
        self._csv_writer = None
        self._csv_file = None

    def _validate_config(self):
        if self.destination == "file":
            if not self.output_file:
                raise ValueError("output_file must be set for file output")
            if self.format not in ("json", "csv", "json-pp"):
                raise ValueError("file output requires format json or csv")
        if self.destination == "websocket":
            if not self.websocket_url:
                raise ValueError("websocket_url required for websocket output")
            if self.format != "json":
                raise ValueError("websocket output must be in json format")
        if self.destination == "stdout" and self.format not in ("csv", "json", "json-pp"):
            raise ValueError("stdout output must be csv or json")

    def write(self, data):
        output = {k: data.get(k, None) for k in self.fields}
        if self.destination == "stdout":
            self._write_stdout(output)
        elif self.destination == "file":
            self._write_file(output)
        elif self.destination == "websocket":
            self._write_websocket(output)
        else:
            raise ValueError(f"Unknown output destination: {self.destination}")


    def _write_stdout(self, output):
        if self.format == "json":
            print(json.dumps(output, ensure_ascii=False))
        elif self.format == "json-pp":
            print(json.dumps(output, indent=2, ensure_ascii=False))
        elif self.format == "csv":
            if self._csv_writer is None:
                self._csv_writer = csv.DictWriter(sys.stdout, fieldnames=self.fields)
                self._csv_writer.writeheader()
            self._csv_writer.writerow(output)
        if self.newline_flush:
            sys.stdout.flush()


    def _write_file(self, output):
        if self.format == "json":
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(output, ensure_ascii=False) + "\n")
                if self.newline_flush:
                    f.flush()
        elif self.format == "json-pp":
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
                if self.newline_flush:
                    f.flush()
        elif self.format == "csv":
            if self._csv_writer is None:
                self._csv_file = open(self.output_file, "a", newline='', encoding="utf-8")
                self._csv_writer = csv.DictWriter(self._csv_file, fieldnames=self.fields)
                self._csv_writer.writeheader()
            self._csv_writer.writerow(output)
            if self.newline_flush:
                self._csv_file.flush()


    def _write_websocket(self, output):
        # Placeholder for websocket support—can be built out using asyncio + websockets or another framework.
        # For now, just print as if sending.
        print(f"[WS-SEND] {json.dumps(output, ensure_ascii=False)}")

    def close(self):
        if self._csv_file:
            self._csv_file.close()
