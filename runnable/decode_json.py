from __future__ import annotations

from dataclasses import dataclass

@dataclass
class ControlSignals:
    load_enable: bool = False
    load_from_enable: bool = False
    store_enable: bool = False
    alu_enable: bool = False
    alu_op: str | None = None
    read_enable: bool = False
    write_enable: bool = False
    jump: bool = False
    branch: str | None = None
    halt: bool = False
    reg_src: str | None = None
    reg_dest: str | None = None
    immediate: int | None = None
    address: int | None = None
    port: int | None = None
    input_type: str | None = None
    output_type: str | None = None

    def reset(self):
        for field_name in self.__dataclass_fields__:
            if field_name == "halt":
                continue
            value = getattr(self, field_name)
            if isinstance(value, bool):
                setattr(self, field_name, False)
            else:
                setattr(self, field_name, None)


def decode_instr(instruction):
    decoded = {}
    i = 1
    decoded["op"] = instruction.get("opcode")
    decoded["operand1"] = None
    decoded["operand2"] = None
    flag = True
    for arg in instruction.get("args"):
        str_op = "operand" + str(i)
        if "reg" in arg:
            decoded[str_op] = arg["reg"]
        elif "number" in arg:
            decoded[str_op] = int(arg["number"])
        elif "indir_reg" in arg:
            decoded[str_op] = arg["indir_reg"]
            if flag and (decoded["op"] == "set" or decoded["op"] == "save"):
                decoded["op"] += "_addr"
                flag = False
        i += 1
    return decoded


class Decoder:
    def __init__(self):
        self.control_signals = ControlSignals()
        self.operands: dict[str, str] = {}

    def decode_instruction(self, instruction):
        self.control_signals.reset()
        self.operands = {}
        decoded_instr = decode_instr(instruction)

        self.operands["reg_dest"] = decoded_instr["operand1"]
        self.operands["reg_src"] = decoded_instr["operand2"]
        if decoded_instr["op"] in ["printc", "print", "get", "getc"]:
            self.operands["reg_src"] = decoded_instr["operand1"]
        self.operands["immediate"] = decoded_instr["operand2"]
        self.operands["address"] = decoded_instr["operand1"]
        self.operands["port"] = decoded_instr["operand2"]
        self.operands["branch"] = decoded_instr["op"]

        self.control_signals.alu_op = decoded_instr["op"]
        if decoded_instr["op"] == "set":
            self.control_signals.reg_dest = self.operands["reg_dest"]
            self.control_signals.immediate = self.operands["immediate"]
            self.control_signals.load_enable = True

        elif decoded_instr["op"] == "set_addr":
            self.control_signals.reg_dest = self.operands["reg_dest"]
            self.control_signals.reg_src = self.operands["reg_src"]
            self.control_signals.load_from_enable = True

        elif decoded_instr["op"] == "save":
            self.control_signals.reg_src = self.operands["reg_src"]
            self.control_signals.reg_dest = self.operands["reg_dest"]
            self.control_signals.address = self.operands["address"]
            self.control_signals.store_enable = True

        elif decoded_instr["op"] == "save_addr":
            self.control_signals.reg_dest = self.operands["reg_dest"]
            self.control_signals.reg_src = self.operands["reg_src"]
            self.control_signals.store_enable = True

        elif decoded_instr["op"] == "sum":
            self.control_signals.reg_dest = self.operands["reg_dest"]
            self.control_signals.reg_src = self.operands["reg_src"]
            self.control_signals.alu_enable = True
            self.control_signals.alu_op = "add"

        elif decoded_instr["op"] == "sub":
            self.control_signals.reg_dest = self.operands["reg_dest"]
            self.control_signals.reg_src = self.operands["reg_src"]
            self.control_signals.alu_enable = True
            self.control_signals.alu_op = "sub"

        elif decoded_instr["op"] == "mod":
            self.control_signals.reg_dest = self.operands["reg_dest"]
            self.control_signals.reg_src = self.operands["reg_src"]
            self.control_signals.alu_enable = True
            self.control_signals.alu_op = "mod"

        elif decoded_instr["op"] == "cmp":
            self.control_signals.reg_src = self.operands["reg_src"]
            self.control_signals.reg_dest = self.operands["reg_dest"]
            self.control_signals.alu_enable = True
            self.control_signals.alu_op = "cmp"

        elif (decoded_instr["op"] == "jmp" or decoded_instr["op"] == "jeq" or decoded_instr["op"] == "jne" or
              decoded_instr["op"] == "jl"):
            self.control_signals.address = self.operands["address"]
            self.control_signals.branch = decoded_instr["op"]
            self.control_signals.jump = True

        elif decoded_instr["op"] == "get":
            self.control_signals.reg_dest = self.operands["reg_dest"]
            self.control_signals.port = self.operands["port"]
            self.control_signals.input_type = "number"
            self.control_signals.read_enable = True

        elif decoded_instr["op"] == "getc":
            self.control_signals.reg_dest = self.operands["reg_dest"]
            self.control_signals.port = self.operands["port"]
            self.control_signals.input_type = "char"
            self.control_signals.read_enable = True

        elif decoded_instr["op"] == "print":
            self.control_signals.reg_src = self.operands["reg_src"]
            self.control_signals.port = self.operands["port"]
            self.control_signals.output_type = "number"
            self.control_signals.write_enable = True

        elif decoded_instr["op"] == "printc":
            self.control_signals.reg_src = self.operands["reg_src"]
            self.control_signals.port = self.operands["port"]
            self.control_signals.output_type = "char"
            self.control_signals.write_enable = True

        elif decoded_instr["op"] == "stop":
            self.control_signals.halt = True

        return self.control_signals.__dict__.copy()
