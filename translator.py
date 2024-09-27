import argparse
import re
import sys
from pathlib import Path
from typing import Tuple

OPCODE = {
    "set": "0000",
    "set_addr": "0001",
    "save": "0010",
    "save_addr": "0011",
    "sum": "0100",
    "sub": "0101",
    "mul": "0110",
    "cmp": "0111",
    "jmp": "1000",
    "jeq": "1001",
    "jne": "1010",
    "print": "1100",
    "printc": "1101",
    "get": "1110",
    "getc": "1111",
    "break": "1111"
}

REG = {"rg1": "0000000001", "rg2": "0000000010", "rg3": "0000000011", "rg4": "0000000100"}

OPCODE_DICT = {
    "z_op": {
        "break"
    },
    "o_op": {
        "jeq",
        "jne",
        "jmp"
    }
}

CODE_START = 0
DATA_START = 0


def refactor_lines(code: str):
    lines = []
    for line in code.splitlines():
        line = line.strip()
        lines.append(line)

    fcode = "\n".join(lines)
    fcode = re.sub(r" +", " ", fcode)

    return fcode


def parse_word(word: str) -> Tuple[list, int]:
    list_chars = []
    offset = 0
    for char in word:
        list_chars.append(ord(char))
        offset += 1
    list_chars.append(0)
    offset += 1
    return list_chars, offset

data_list = []
def set_labels(code: str) -> Tuple[dict, dict]:
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
            i = i + 1
        if line == "section .text":
            start_flag = True
            data_flag = False
        if data_flag:
            words = line.split(" ")
            if (len(words) > 1):
                data[words[0]] = j
                if words[1].isdigit():
                    data_list.append(int(words[1]))
                else:
                    word = line[(len(words[0]) + 2):-1]
                    char_list, offset = parse_word(word)
                    j += offset
                    data_list.extend(char_list)
        if line == "section .data":
            data_flag = True

    return labels, data


def parse_code(code: str):
    code = refactor_lines(code)
    labels, data = set_labels(code)

    data_str = "\"data\": " + data_list.__str__()
    flag = False
    command_str = "\"text\": ["
    for line in code.splitlines():
        if re.match(r"^(\w+):", line):
            continue
        words = line.split(" ")
        if (words[0] in OPCODE):
            if flag:
                command_str += ", "
            else:
                flag = True
            #print(line + "\n")
            if (words[0] in OPCODE_DICT["z_op"]):
                str = "{\"opcode\": \"" + words[0] + "\", \"args\": []}"
                command_str += str
            elif (words[0] in OPCODE_DICT["o_op"]):
                str = "{\"opcode\": \"" + words[0] + "\", \"args\": ["
                if words[1] in REG:
                    str += "{\"reg\": \"" + words[1] + "\"}]}"
                elif words[1] in labels.keys():
                    str += "{\"number\": \"" + f"{labels[words[1]]}" + "\"}]}"
                elif words[1] in data.keys():
                    str += "{\"number\": \"" + f"{data[words[1]]}" + "\"}]}"
                elif words[1].startswith("(R"):
                    str += "{\"indir_reg\": \"" + words[1][1:-1] + "\"}]}"
                else:
                    str += "{\"number\": \"" + words[1] + "\"}]}"
                command_str += str
            else:
                words[1] = words[1][:-1]
                str = "{\"opcode\": \"" + words[0] + "\", \"args\": ["
                if words[1] in REG:
                    str += "{\"reg\": \"" + words[1] + "\"}, "
                elif words[1] in labels.keys():
                    str += "{\"number\": \"" + f"{labels[words[1]]}" + "\"}, "
                elif words[1] in data.keys():
                    str += "{\"number\": \"" + f"{data[words[1]]}" + "\"}, "
                elif words[1].startswith("(R"):
                    str += "{\"indir_reg\": \"" + words[1][1:-1] + "\"}]}"
                else:
                    str += "{\"number\": \"" + words[1] + "\"}, "
                if words[2] in REG:
                    str += "{\"reg\": \"" + words[2] + "\"}]}"
                elif words[2] in labels.keys():
                    str += "{\"number\": \"" + f"{labels[words[2]]}" + "\"}]}"
                elif words[2] in data.keys():
                    str += "{\"number\": \"" + f"{data[words[2]]}" + "\"}]}"
                elif words[2].startswith("(r"):
                    str += "{\"indir_reg\": \"" + words[2][1:-1] + "\"}]}"
                else:
                    str += "{\"number\": \"" + words[2] + "\"}]}"
                command_str += str
    command_str += "]"
    json_str = "{" + data_str + ", " + command_str + "}"

    return json_str


def main(input_file, target_file):
    with open(input_file, encoding="utf-8") as infile:
        asm_code = infile.read()

    json_string = parse_code(asm_code)

    with open(target_file, "w") as outfile:
        outfile.write(json_string)


if __name__ == "__main__":
    input_file = sys.argv[1]
    target_file = sys.argv[2]
    main(input_file, target_file)
