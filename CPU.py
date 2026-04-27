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


class MicroInstruction:
    def __init__(self,
                 src_a=None,
                 src_b=None,
                 alu_op=None,
                 reg_write=0,
                 mem_read=0,
                 mem_write=0,
                 use_imm=0,
                 write_flags=0,
                 pc_write=0,
                 cond=None,
                 jump=0,
                 next_addr=None):

        self.src_a = src_a
        self.src_b = src_b
        self.alu_op = alu_op

        self.reg_write = reg_write
        self.mem_read = mem_read
        self.mem_write = mem_write

        self.use_imm = use_imm
        self.write_flags = write_flags

        self.pc_write = pc_write
        self.cond = cond

        self.jump = jump
        self.next_addr = next_addr


class CPU:
    def __init__(self,  instr_mem_size=256, data_mem_size=256):
        self.tick = 0

        self.MP = 0
        self.PC = 0
        self.IR = 0

        self.regs = Register()
        self.instr_mem = Memory(instr_mem_size)
        self.data_mem  = Memory(data_mem_size)
        self.micro_mem = [None] * 512

        self.halt = False
        self.set_microcode()

    def set_microcode(self):

        self.micro_mem[0x01 * 4] = MicroInstruction(
            jump=1,
            next_addr="HALT"
        )

        base = 0x20 * 4
        self.micro_mem[base] = MicroInstruction(src_a="rs1", src_b="rs2", alu_op="ADD", reg_write=1)
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        # SUB
        base = 0x21 * 4
        self.micro_mem[base] = MicroInstruction(src_a="rs1", src_b="rs2", alu_op="SUB", reg_write=1)
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        # MUL
        base = 0x22 * 4
        self.micro_mem[base] = MicroInstruction(src_a="rs1", src_b="rs2", alu_op="MUL", reg_write=1)
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        # DIV
        base = 0x23 * 4
        self.micro_mem[base] = MicroInstruction(src_a="rs1", src_b="rs2", alu_op="DIV", reg_write=1)
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        # --- Арифметика (Reg-Imm) ---
        # ADDI
        base = 0x24 * 4
        self.micro_mem[base] = MicroInstruction(src_a="rs1", use_imm=1, alu_op="ADD", reg_write=1)
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        # SUBI
        base = 0x25 * 4
        self.micro_mem[base] = MicroInstruction(src_a="rs1", use_imm=1, alu_op="SUB", reg_write=1)
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        # --- Данные ---
        # LOADI (Запись imm в rd)
        base = 0x10 * 4
        self.micro_mem[base] = MicroInstruction(src_a="imm", reg_write=1)
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)


        # LOAD (Чтение из памяти)
        base = 0x11 * 4
        self.micro_mem[base] = MicroInstruction(src_a="rs1", use_imm=1, alu_op="ADD")  # Адрес = rs1 + imm
        self.micro_mem[base + 1] = MicroInstruction(mem_read=1, reg_write=1)  # Читаем
        self.micro_mem[base + 2] = MicroInstruction(jump=1, next_addr=0)  # Конец

        # STORE (Запись в память)
        base = 0x12 * 4
        self.micro_mem[base] = MicroInstruction(src_a="rs1", use_imm=1, alu_op="ADD")  # Адрес = rs1 + imm
        self.micro_mem[base + 1] = MicroInstruction(mem_write=1)  # Пишем
        self.micro_mem[base + 2] = MicroInstruction(jump=1, next_addr=0)

        # MOV
        base = 0x30 * 4
        self.micro_mem[base] = MicroInstruction(src_a="rs1", reg_write=1)
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        # CMP (Только флаги)
        base = 0x31 * 4
        self.micro_mem[base] = MicroInstruction(src_a="rs1", src_b="rs2", alu_op="SUB")
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        # --- Прыжки ---
        # JMP
        base = 0x50 * 4
        self.micro_mem[base] = MicroInstruction(pc_write=1)
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        # JZ
        base = 0x51 * 4
        self.micro_mem[base] = MicroInstruction(pc_write=1, cond="Z")
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        # JNZ
        base = 0x52 * 4
        self.micro_mem[base] = MicroInstruction(pc_write=1, cond="NZ")
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)


    # def set_microcode(self):
    #     self.microcode.add(0x00, [NOP()])
    #     self.microcode.add(0x01, [HALT()])
    #
    #     self.microcode.add(0x10, [LOADI()])
    #     self.microcode.add(0x11, [LOAD()])
    #     self.microcode.add(0x12, [STORE()])
    #
    #     self.microcode.add(0x20, [ADD()])
    #     self.microcode.add(0x21, [SUB()])
    #     self.microcode.add(0x22, [MUL()])
    #     self.microcode.add(0x23, [DIV()])
    #     self.microcode.add(0x24, [ADDI()])
    #     self.microcode.add(0x25, [SUBI()])
    #
    #     self.microcode.add(0x30, [MOV()])
    #
    #     self.microcode.add(0x40, [AND()])
    #     self.microcode.add(0x41, [OR()])
    #     self.microcode.add(0x42, [XOR()])
    #
    #     self.microcode.add(0x50, [JMP()])
    #     self.microcode.add(0x51, [JZ()])
    #     self.microcode.add(0x52, [JNZ()])

    def step(self):
        if not self.halt:
            self.micro_step()

    def get_src(self, name):
        if name == "rs1":
            return self.regs[(self.IR >> 16) & 0xF]

        if name == "rs2":
            return self.regs[(self.IR >> 12) & 0xF]

        if name == "imm":
            return self.IR & 0xFFF

        if name == "PC":
            return self.PC

        return 0

    def micro_step(self):
        if self.MP == 0:
            self.IR = self.instr_mem.read(self.PC)
            self.MP = 1
        elif self.MP == 1:
            self.PC += 1
            self.MP = 10
        elif self.MP == 10:
            opcode = (self.IR >> 24) & 0xFF
            self.MP = opcode * 4

        else:
            micro = self.micro_mem[self.MP]
            if micro is None:
                self.MP = 0
                return

            if micro.next_addr == "HALT":
                self.halt = True
                return

            a = self.get_src(micro.src_a)
            b = self.IR & 0xFFF if micro.use_imm else self.get_src(micro.src_b)

            if micro.alu_op:
                res = self.ALU(micro.alu_op, a, b)
            else:
                res = a

            if micro.reg_write:
                rd = (self.IR >> 20) & 0x0F
                self.regs[rd] = res

            if micro.mem_write:
                self.data_mem.write(res, self.get_src("rs2"))

            if micro.mem_read:
                self.regs[(self.IR >> 20) & 0x0F] = self.data_mem.read(res)

            if micro.pc_write:
                cond_met = True
                if micro.cond == "Z": cond_met = (self.regs.flags["Z"] == 1)
                if micro.cond == "NZ": cond_met = (self.regs.flags["Z"] == 0)
                if cond_met:
                    self.PC = self.IR & 0xFFF

            if micro.jump:
                self.MP = micro.next_addr
            else:
                self.MP += 1

        self.tick += 1

    def ALU(self, op, a, b):
        if op == "ADD":
            res = a + b
        elif op == "SUB":
            res = a - b
        elif op == "MUL":
            res = a * b
        elif op == "DIV":
            res = a // b if b != 0 else 0
        elif op == "AND":
            res = a & b
        elif op == "OR":
            res = a | b
        elif op == "XOR":
            res = a ^ b
        else:
            res = a

        self.regs.flags["Z"] = int(res == 0)
        self.regs.flags["N"] = int(res < 0)

        return res
