from __future__ import annotations

import re
import sys

OPCODES = [
    "set",
    "set_addr",
    "save",
    "save_addr",
    "sum",
    "sub",
    "mod",
    "cmp",
    "jmp",
    "jeq",
    "jne",
    "print",
    "printc",
    "get",
    "getc",
    "break",
    "jl",
]

REG = ["rg1", "rg2", "rg3", "rg4"]

OPCODE_DICT = {"z_op": {"break"}, "o_op": {"jeq", "jne", "jmp", "jl"}}

CODE_START = 0
DATA_START = 0


def refactor_lines(code: str):
    lines = []
    for line in code.splitlines():
        line = line.strip().split(";")[0]
        if line != "":
            lines.append(line)
    return re.sub(r" +", " ", "\n".join(lines))


def parse_word(word: str) -> tuple[list, int]:
    list_chars = []
    offset = 0
    for char in word:
        list_chars.append(ord(char))
        offset += 1
    list_chars.append(0)
    offset += 1
    return list_chars, offset


data_list = []


def set_labels(code: str) -> tuple[dict, dict]:
    labels = {}
    data = {}

    i = CODE_START
    j = DATA_START

    start_flag = False
    data_flag = False
    for line in code.splitlines():
        if start_flag:
            if re.match(r"^(\w+):", line):
                labels[line.partition(":")[0].strip()] = i
            else:
                i = i + 1
        if line == "section .text":
            start_flag = True
            data_flag = False
        if data_flag:
            words = line.split(" ")
            if len(words) > 1:
                data[words[0]] = j
                if words[1].isdigit():
                    data_list.append(int(words[1]))
                    j += 1
                else:
                    word = line[(len(words[0]) + 2) : -1]
                    char_list, offset = parse_word(word)
                    j += offset
                    data_list.extend(char_list)
        if line == "section .data":
            data_flag = True

    return labels, data


def parse_code(code: str):
    code = refactor_lines(code)
    labels, data = set_labels(code)

    data_str = '"data": ' + data_list.__str__()
    flag = False
    command_str = '"text": ['
    flag_text = True
    for line in code.splitlines():
        if line == "section .text":
            flag_text = False
        if flag_text:
            continue
        if re.match(r"^(\w+):", line):
            continue
        words = line.split(" ")
        if words[0] in OPCODES:
            if flag:
                command_str += ", "
            else:
                flag = True
            if words[0] in OPCODE_DICT["z_op"]:
                str_building_json = '{"opcode": "' + words[0] + '", "args": []}'
                command_str += str_building_json
            elif words[0] in OPCODE_DICT["o_op"]:
                str_building_json = '{"opcode": "' + words[0] + '", "args": ['
                if words[1] in REG:
                    str_building_json += '{"reg": "' + words[1] + '"}]}'
                elif words[1] in labels.keys():
                    str_building_json += '{"number": "' + f"{labels[words[1]]}" + '"}]}'
                elif words[1] in data.keys():
                    str_building_json += '{"number": "' + f"{data[words[1]]}" + '"}]}'
                elif words[1].startswith("(R"):
                    str_building_json += '{"indir_reg": "' + words[1][1:-1] + '"}]}'
                else:
                    str_building_json += '{"number": "' + words[1] + '"}]}'
                command_str += str_building_json
            else:
                words[1] = words[1][:-1]
                str_building_json = '{"opcode": "' + words[0] + '", "args": ['
                if words[1] in REG:
                    str_building_json += '{"reg": "' + words[1] + '"}, '
                elif words[1] in labels.keys():
                    str_building_json += '{"number": "' + f"{labels[words[1]]}" + '"}, '
                elif words[1] in data.keys():
                    str_building_json += '{"number": "' + f"{data[words[1]]}" + '"}, '
                elif words[1].startswith("(r"):
                    str_building_json += '{"indir_reg": "' + words[1][1:-1] + '"}, '
                else:
                    str_building_json += '{"number": "' + words[1] + '"}, '
                if words[2] in REG:
                    str_building_json += '{"reg": "' + words[2] + '"}]}'
                elif words[2] in labels.keys():
                    str_building_json += '{"number": "' + f"{labels[words[2]]}" + '"}]}'
                elif words[2] in data.keys():
                    str_building_json += '{"number": "' + f"{data[words[2]]}" + '"}]}'
                elif words[2].startswith("(r"):
                    str_building_json += '{"indir_reg": "' + words[2][1:-1] + '"}]}'
                else:
                    str_building_json += '{"number": "' + words[2] + '"}]}'
                command_str += str_building_json
    command_str += "]"

    return "{" + data_str + ", " + command_str + "}"


class Translator:
    def __init__(self):
        self.json_string = None

    def read_file(self, inputf):
        data_list.clear()
        with open(inputf, encoding="utf-8") as infile:
            asm_code = infile.read()
        self.json_string = parse_code(asm_code)

    def get_json(self):
        return self.json_string

    def write_file(self, target):
        if self.json_string is not None:
            with open(target, "w") as outfile:
                outfile.write(self.json_string)


def main(in_file, t_file):
    translator = Translator()
    translator.read_file(in_file)
    translator.write_file(t_file)


if __name__ == "__main__":
    input_file = sys.argv[1]
    target_file = sys.argv[2]
    main(input_file, target_file)
