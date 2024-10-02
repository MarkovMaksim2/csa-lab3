class InputDevice:
    def __init__(self, data, memory, bind1, bind2):
        self.buffer = {0: data, 1: None}
        self.memory = memory
        self.bind1 = bind1
        self.bind2 = bind2

    def read(self, type, port):
        bind = self.bind1 if port == 0 else self.bind2

        if self.buffer.get(port):
            if type == "number":
                word = ""
                while True:
                    tmp = self.buffer[port].pop(0)
                    if tmp == chr(0):
                        break
                    word += tmp
                self.memory[bind] = int(word)
            self.memory[bind] = ord(self.buffer[port].pop(0))
