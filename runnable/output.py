class OutputDevice:
    def __init__(self, memory, bind1, bind2):
        self.buffer = {}
        self.file = [open('port1.txt', 'w'), open('port2.txt', 'w')]
        self.memory = memory
        self.bind1 = bind1
        self.bind2 = bind2

    def write(self, port, type):
        if port not in self.buffer:
            self.buffer[port] = []
        bind = self.bind1 if port == 1 else self.bind2
        data = str(self.memory[bind]) if type == "number" else chr(self.memory[bind] & 0xFF)
        if not (data == 0 or data == '\x00'):
            self.buffer[port].append(data)
            self.file[port - 1].write(data)

    def get_buffer(self, port):
        return self.buffer[port]
