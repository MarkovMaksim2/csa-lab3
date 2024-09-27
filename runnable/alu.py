from numpy import int16


class ALU:
    first_operand: int16 = None

    second_operand: int16 = None

    result: int16 = None

    z_flag: bool = None

    n_flag: bool = None

    def __init__(self) -> None:
        self.first_operand = int16(0)
        self.second_operand = int16(0)
        self.result = int16(0)
        self.z_flag = False
        self.n_flag = False

    def compute(self, op):
        if op == "sum":
            self.result = self.first_operand + self.second_operand
        elif op == "sub":
            self.result = self.second_operand - self.first_operand
        elif op == "cmp":
            self.result = 0
            self.z_flag = self.second_operand == self.first_operand
        elif op == "mul":
            self.result = self.first_operand * self.second_operand
        else:
            self.result = int16(0)

        if self.result < 0:
            self.n_flag = True
        else:
            self.n_flag = False

    def set_first_operand(self, val):
        self.first_operand = int16(val)

    def set_second_operand(self, val):
        self.second_operand = int16(val)

    def get_result(self):
        return self.result

    def get_z(self):
        return self.z_flag

    def get_n(self):
        return self.n_flag
