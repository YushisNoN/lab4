from MICROCOMMANDS import *


class Register:
    def __init__(self, size=8):
        self.R = [0] * size
        self.flags = {"Z": 0, "N": 0}

    def __getitem__(self, key):
        return self.R[key]

    def __setitem__(self, key, value):
        self.R[key] = value
        self.update_flags(value)

    def update_flags(self, value):
        self.flags["Z"] = int(value == 0)
        self.flags["N"] = int(value < 0)

class Memory:
    def __init__(self, size):
        self.mem = [0] * size

    def read(self, addr):
        return self.mem[addr]

    def write(self, addr, value):
        self.mem[addr] = value

class Instruction:
    def __init__(self, word):
        self.word = word
        self.opcode = (word >> 24) & 0xFF
        self.rd     = (word >> 20) & 0x0F
        self.rs1    = (word >> 16) & 0x0F
        self.rs2    = (word >> 12) & 0x0F
        self.imm    = (word)       & 0xFFF

    def __str__(self):
        return (f"{'Field':<8} {'Decimal':<10} {'Binary':<20}\n"
                f"{'-' * 40}\n"
                f"{'opcode':<8} {self.opcode:<10} {self.opcode:08b}\n"
                f"{'rd':<8} {self.rd:<10} {self.rd:04b}\n"
                f"{'rs1':<8} {self.rs1:<10} {self.rs1:04b}\n"
                f"{'rs2':<8} {self.rs2:<10} {self.rs2:04b}\n"
                f"{'imm':<8} {self.imm:<10} {self.imm:012b}\n"
                f"{'word':<8} {self.word:<10} {self.word:032b}")



class Microcode:
    def __init__(self):
        self.table = dict()

    def add(self, opcode, steps):
        self.table[opcode] = steps

    def get_steps(self, opcode):
        return self.table.get(opcode, [])


class CPU:
    def __init__(self,  instr_mem_size=256, data_mem_size=256):
        self.IP = 0
        self.tick = 0
        self.regs = Register()
        self.instr_mem = Memory(instr_mem_size)
        self.data_mem  = Memory(data_mem_size)
        self.microcode = Microcode()
        self.halt = False
        self.set_microcode()

    def set_microcode(self):
        self.microcode.add(0x00, [NOP()])
        self.microcode.add(0x01, [HALT()])

        self.microcode.add(0x10, [LOADI()])
        self.microcode.add(0x11, [LOAD()])
        self.microcode.add(0x12, [STORE()])

        self.microcode.add(0x20, [ADD()])
        self.microcode.add(0x21, [SUB()])
        self.microcode.add(0x22, [MUL()])
        self.microcode.add(0x23, [DIV()])
        self.microcode.add(0x24, [ADDI()])
        self.microcode.add(0x25, [SUBI()])

        self.microcode.add(0x30, [MOV()])

        self.microcode.add(0x40, [AND()])
        self.microcode.add(0x41, [OR()])
        self.microcode.add(0x42, [XOR()])

        self.microcode.add(0x50, [JMP()])
        self.microcode.add(0x51, [JZ()])
        self.microcode.add(0x52, [JNZ()])

    def fetch(self):
        word = self.instr_mem.read(self.IP)
        self.IP += 1
        return Instruction(word)

    def execute_step(self):
        if self.halt:
            return

        instruction = self.fetch()
        steps = self.microcode.get_steps(instruction.opcode)

        for step in steps:
            print(instruction, step)
            step(self, instruction)

        self.tick += 1

