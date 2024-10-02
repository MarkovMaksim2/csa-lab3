from numpy import int16


class ALU:
    def __init__(self) -> None:
        self.first_operand = int16(0)
        self.second_operand = int16(0)
        self.result = int16(0)
        self.z_flag = False
        self.n_flag = False

    def compute(self, op):
        if op == "add":
            self.result = self.first_operand + self.second_operand
        elif op == "sub":
            self.result = self.second_operand - self.first_operand
        elif op == "cmp":
            self.result = self.second_operand - self.first_operand
        elif op == "mod":
            self.result = self.second_operand % self.first_operand
        else:
            self.result = int16(0)
        self.z_flag = self.result == 0
        self.n_flag = self.result < 0

    def set_first_operand(self, val):
        self.first_operand = val

    def set_second_operand(self, val):
        self.second_operand = val

    def get_result(self):
        return self.result

    def get_z(self):
        return self.z_flag

    def get_n(self):
        return self.n_flag
