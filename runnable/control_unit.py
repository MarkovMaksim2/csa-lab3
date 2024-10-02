import logging
from runnable.decode_json import Decoder
from runnable.clock import Clock

clock = Clock()

class ControlUnit:
    def __init__(self, datapath, instructions_mem):
        self.instructions_mem = instructions_mem
        self.pc = 0
        self.datapath = datapath
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename="main.log", encoding="utf-8", level=logging.DEBUG, format='%(message)s')
        self.stopped = False
        self.instruction_stage = "FETCH"
        self.current_instruction = None
        self.control_signals = None
        self.instr_cnt = 0
        self.tick = None
        self.decoder = Decoder()

    def fetch_instruction(self):
        if self.pc < len(self.instructions_mem):
            self.current_instruction = self.instructions_mem[self.pc]
            self.instruction_stage = "DECODE"
        else:
            self.stopped = True

    def decode_instruction(self):
        self.control_signals = self.decoder.decode_instruction(self.current_instruction) #generate_control_signals(op_code, reg_f, reg_s, immediate)

    def execute_instruction(self):
        if self.control_signals:
            if self.control_signals["halt"]:
                self.stopped = True
                return
            if self.control_signals["alu_enable"]:
                self.datapath.use_alu(self.control_signals)
            if self.control_signals["jump"]:
                self.branch_exec()
        else:
            pass

    def branch_exec(self):
        branch = self.control_signals["branch"]
        addr = self.control_signals["address"]
        if branch == "jmp":
            self.pc = addr
            self.instruction_stage = "FETCH"
        elif branch == "jeq":
            if self.datapath.get_z():
                self.pc = addr
                self.instruction_stage = "FETCH"
            else:
                self.pc = self.pc + 1
        elif branch == "jne":
            if not self.datapath.get_z():
                self.pc = addr
                self.instruction_stage = "FETCH"
            else:
                self.pc = self.pc + 1
        elif branch == "jl":
            if self.datapath.get_n():
                self.pc = addr
                self.instruction_stage = "FETCH"
            else:
                self.pc = self.pc + 1
                
    def exec(self):
        while not self.stopped:
            if not self.stopped:
                tick = clock.tick()
                if self.instruction_stage == "FETCH":
                    self.fetch_instruction()
                    self.instr_cnt += 1
                    self.log(self.current_instruction, self.instr_cnt)
                    self.instruction_stage = "DECODE"
                elif self.instruction_stage == "DECODE":
                    self.decode_instruction()
                    self.instruction_stage = "EXECUTE"
                elif self.instruction_stage == "EXECUTE":
                    self.execute_instruction()
                    if not self.instruction_stage == "FETCH":
                        self.instruction_stage = "MEMORY"
                elif self.instruction_stage == "MEMORY":
                    self.memory_access()
                    self.instruction_stage = "WRITEBACK"
                elif self.instruction_stage == "WRITEBACK":
                    self.write_back()
                    self.instruction_stage = "FETCH"
        print(tick)
        print("\n")
        print(self.instr_cnt)


    def memory_access(self):
        if self.control_signals:
            if (
                    self.control_signals["load_from_enable"]
                    or self.control_signals["store_enable"]
            ):
                self.datapath.load_memory(self.control_signals)
        else:
            pass

    def write_back(self):
        if self.control_signals:
            self.datapath.perform_register_write(self.control_signals)
            self.datapath.perform_io_operation(self.control_signals)
            if not self.control_signals.get("jump", False):
                self.pc = self.pc + 1
        else:
            pass

    def log(self, instruction, instruction_cnt):
        op = instruction.get('opcode')
        self.logger.debug(
            f"INSTR={instruction_cnt} | OP={op} | PC={self.pc} | rg1={self.datapath.address_register['rg1']} | rg2={self.datapath.address_register['rg2']} | rg3={self.datapath.address_register['rg3']} | rg4={self.datapath.address_register['rg4']} |  data={self.datapath.memory.memory}"
        )
