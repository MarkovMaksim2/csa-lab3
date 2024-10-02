from __future__ import annotations

from runnable.alu import ALU
from runnable.input import InputDevice
from runnable.output import OutputDevice


class Memory:
    def __init__(self, data: list[int]):
        self.value = 0
        self.memory = 1024 * [0]
        for i in range(0, len(data)):
            self.memory[i] = data[i]


class DataPath:
    def __init__(self, data: list[int], inputdp):
        self.memory = Memory(data)
        self.alu = ALU()
        self.address_register = {"rg1": 0, "rg2": 0, "rg3": 0, "rg4": 0}
        self.data_register = None
        self.operand_register = None
        self.value_buffer = None
        self.input_device = InputDevice(inputdp, self.memory.memory, 1019, 1020)
        self.output_device = OutputDevice(self.memory.memory, 1021, 1022)

    def get_value(self, val):
        if val in self.address_register:
            return self.address_register[val]
        if isinstance(val, int):
            return val
        return int(val)

    def use_alu(self, control_signal):
        op = control_signal.get("alu_op", None)
        src = control_signal.get("reg_src", None)
        dst = control_signal.get("reg_dest", None)

        self.alu.set_first_operand(self.get_value(self.address_register[src]))
        self.alu.set_second_operand(self.get_value(self.address_register[dst]))

        self.alu.compute(op)

    def get_z(self):
        return self.alu.get_z()

    def get_n(self):
        return self.alu.get_n()

    def load_memory(self, control_signal):
        load_from_enable = control_signal.get("load_from_enable", False)
        store_enable = control_signal.get("store_enable", False)
        reg_src = control_signal.get("reg_src", "")
        reg_dest = control_signal.get("reg_dest", "")
        address = control_signal.get("address", None)

        if load_from_enable:
            self.value_buffer = self.memory.memory[self.address_register[reg_src]]
        if store_enable:
            if address is not None:
                value = self.address_register[reg_dest]
                self.memory.memory[address] = value
            else:
                value = self.address_register[reg_dest]
                self.memory.memory[self.address_register[reg_src]] = value

    def perform_register_write(self, control_signals):
        load_enable = control_signals.get("load_enable", False)
        alu_enable = control_signals.get("alu_enable", False)
        reg_dest = control_signals.get("reg_dest", "")
        immediate = control_signals.get("immediate", None)

        if load_enable:
            self.address_register[reg_dest] = self.get_value(immediate)
        elif alu_enable:
            alu_op = control_signals.get("alu_op", None)
            if alu_op != "cmp":
                self.address_register[reg_dest] = self.alu.get_result()
        elif self.value_buffer is not None:
            self.address_register[reg_dest] = self.value_buffer
            self.value_buffer = None

    def perform_io_operation(self, control_signals):
        read_enable = control_signals.get("read_enable", False)
        write_enable = control_signals.get("write_enable", False)
        reg_src = control_signals.get("reg_src", "")
        reg_dest = control_signals.get("reg_dest", "")
        port = control_signals.get("port", None)
        input_type = control_signals.get("input_type", None)
        output_type = control_signals.get("output_type", None)
        if read_enable:
            self.read_mem(reg_dest, port, input_type)
        if write_enable:
            self.write_mem(reg_src, port, output_type)

    def read_mem(self, reg_dest, port, input_type):
        self.input_device.read(input_type, port)
        data = self.memory.memory[1019 if port == 0 else 1020]
        if data is not None:
            self.address_register[reg_dest] = data
        else:
            raise Exception("[Error] Буфер ввода пуст. Остановка выполнения.")

    def write_mem(self, reg_src, port, output_type):
        self.memory.memory[1021 if port == 1 else 1022] = self.address_register[reg_src]
        self.output_device.write(port, output_type)

    def test_get_buffer(self, port):
        return self.output_device.get_buffer(port)
