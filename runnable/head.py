from __future__ import annotations

import json
import sys

from runnable.control_unit import ControlUnit
from runnable.datapath import DataPath


def replace_escape_sequences(input_data: list[str]) -> list[str]:
    i = len(input_data) - 1
    while i > 0:
        if input_data[i] == "n" and input_data[i - 1] == "\\":
            input_data.pop(i - 1)
            input_data[i - 1] = "\n"
            i -= 1
        i -= 1

    return input_data


def main(asm_file, input_file):
    with open(asm_file) as file:
        json_file = json.load(file)

    with open(input_file) as file:
        input_data = replace_escape_sequences(list(file.read().strip() + chr(0)))

    data_path = DataPath(json_file.get("data", []), input_data)
    control_unit = ControlUnit(data_path, json_file.get("text", []))

    control_unit.exec()


if __name__ == "__main__":
    input_file = sys.argv[1]
    target_file = sys.argv[2]
    main(input_file, target_file)
