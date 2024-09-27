from numpy import int16

from runnable.alu import ALU


class Memory:
    memory: list[int16] = []

    value: int16 = 0

    def __init__(self, data: list[int16]):
        for element in data:
            self.memory.append(int16(element))
        self.memory.extend([int16(0)] * (1024 - len(data)))
        self.value = int16(0)


class DataPath:
    memory: Memory = None

    address_register: dict = {"rg1": 0, "rg2": 0, "rg3": 0, "rg4": 0}

    data_register: int16 = None

    operand_register: int16 = None

    alu: ALU = None

    def __init__(self, data: list[int16], input_tokens: list[str]):
        self.data_memory = Memory(data)
        self.alu = ALU()

    def use_alu(self, control_signal):
        op = control_signal.get("op", None)
        src = control_signal.get("reg_f", None)
        dst = control_signal.get("reg_s", None)

        self.alu.set_first_operand(self.address_register[src])
        self.alu.set_second_operand(self.address_register[dst])

        self.alu.compute(op)

    def get_z(self):
        return self.alu.get_z()

    def get_n(self):
        return self.alu.get_n()

    #def load_memory(self, control_signal):


