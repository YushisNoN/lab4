class Register:
    def __init__(self, size=8):
        self.R = [0] * size
        self.flags = {"Z": 0, "N": 0, "V": 0, "C": 0}

    def __getitem__(self, key):
        return self.R[key]

    def __setitem__(self, key, value):
        self.R[key] = value

    def update_flags(self, value, overflow=0):
        self.flags["Z"] = int(value == 0)
        self.flags["N"] = int((value >> 31) & 1)
        self.flags["V"] = int(overflow)


class Memory:
    def __init__(self, size):
        self.mem = [0] * size

    def read(self, addr):
        if addr < 0 or addr >= len(self.mem):
            raise Exception("Memory access violation")
        return self.mem[addr]

    def write(self, addr, value):
        self.mem[addr] = value


class Instruction:
    def __init__(self, word):
        self.word = word
        self.opcode = (word >> 24) & 0xFF
        self.rd = (word >> 20) & 0x0F
        self.rs1 = (word >> 16) & 0x0F
        self.rs2 = (word >> 12) & 0x0F
        self.imm = (word) & 0xFFF

    def __str__(self):
        return (
            f"{'Field':<8} {'Decimal':<10} {'Binary':<20}\n"
            f"{'-' * 40}\n"
            f"{'opcode':<8} {self.opcode:<10} {self.opcode:08b}\n"
            f"{'rd':<8} {self.rd:<10} {self.rd:04b}\n"
            f"{'rs1':<8} {self.rs1:<10} {self.rs1:04b}\n"
            f"{'rs2':<8} {self.rs2:<10} {self.rs2:04b}\n"
            f"{'imm':<8} {self.imm:<10} {self.imm:012b}\n"
            f"{'word':<8} {self.word:<10} {self.word:032b}\n"
        )


class MicroInstruction:
    def __init__(
        self,
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
        next_addr=None,
        mem_data=None,
        mem_addr=None,
        sp_dec=0,
        sp_inc=0,
    ):

        self.src_a = src_a
        self.src_b = src_b
        self.alu_op = alu_op

        self.reg_write = reg_write
        self.mem_read = mem_read
        self.mem_write = mem_write
        self.mem_data = mem_data
        self.use_imm = use_imm
        self.write_flags = write_flags

        self.pc_write = pc_write
        self.cond = cond
        self.mem_addr = mem_addr

        self.jump = jump
        self.next_addr = next_addr

        self.sp_dec = sp_dec
        self.sp_inc = sp_inc


class CPU:
    def __init__(self, instr_mem_size=256, data_mem_size=256):
        self.tick = 0

        self.MP = 0
        self.PC = 0
        self.IR = 0

        self.micro_running = False
        self.micro_mp = 0
        self.micro_current_instr = None
        self.micro_rs1 = 0
        self.micro_rs2 = 0
        self.micro_imm = 0
        self.micro_result = 0

        self.stall = False
        self.flush = False
        self.total_cycles = 0
        self.stall_cycles = 0

        self.pending_mem_addr = 0
        self.pending_mem_data = 0
        self.pending_is_mem_op = 0

        self.regs = Register(size=16)
        self.instr_mem = Memory(instr_mem_size)
        self.data_mem = Memory(data_mem_size)
        self.micro_mem = [None] * 512

        self.IN = 255
        self.OUT = 254

        self.SP = len(self.data_mem.mem) - 1

        self.input_buffer = []
        self.output_buffer = []
        self.buffer_reg = 0

        self.halt = False
        self.set_microcode()

    def set_microcode(self):

        self.micro_mem[0x01 * 4] = MicroInstruction(jump=1, next_addr="HALT")

        base = 0x02 * 4
        self.micro_mem[base] = MicroInstruction(
            src_a="rs1", src_b="rs2", alu_op="SUB", reg_write=1
        )
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x20 * 4
        self.micro_mem[base] = MicroInstruction(
            src_a="rs1", src_b="rs2", alu_op="ADD", reg_write=1, write_flags=1
        )
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x21 * 4
        self.micro_mem[base] = MicroInstruction(
            src_a="rs1", src_b="rs2", alu_op="SUB", reg_write=1, write_flags=1
        )
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x22 * 4
        self.micro_mem[base] = MicroInstruction(
            src_a="rs1", src_b="rs2", alu_op="MUL", reg_write=1, write_flags=1
        )
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x23 * 4
        self.micro_mem[base] = MicroInstruction(
            src_a="rs1", src_b="rs2", alu_op="DIV", reg_write=1, write_flags=1
        )
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x24 * 4
        self.micro_mem[base] = MicroInstruction(
            src_a="rs1", use_imm=1, alu_op="ADD", reg_write=1, write_flags=1
        )
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x25 * 4
        self.micro_mem[base] = MicroInstruction(
            src_a="rs1", use_imm=1, alu_op="SUB", reg_write=1, write_flags=1
        )
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x10 * 4
        self.micro_mem[base] = MicroInstruction(src_a="rs1", use_imm=1, alu_op="ADD")
        self.micro_mem[base + 1] = MicroInstruction(mem_read=1, reg_write=1)
        self.micro_mem[base + 2] = MicroInstruction(jump=1, next_addr=0)

        base = 0x11 * 4
        self.micro_mem[base] = MicroInstruction(src_a="imm", reg_write=1)
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x12 * 4
        self.micro_mem[base] = MicroInstruction(mem_write=1, mem_data="rs1")
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x30 * 4
        self.micro_mem[base] = MicroInstruction(src_a="rs1", reg_write=1)
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x31 * 4
        self.micro_mem[base] = MicroInstruction(
            src_a="rs1", src_b="rs2", alu_op="SUB", reg_write=0, write_flags=1
        )
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        for op_name, op_code in [("AND", 0x40), ("OR", 0x41), ("XOR", 0x42)]:
            base = op_code * 4
            self.micro_mem[base] = MicroInstruction(
                src_a="rs1", src_b="rs2", alu_op=op_name, reg_write=1
            )
            self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x50 * 4
        self.micro_mem[base] = MicroInstruction(jump=1, next_addr="IMM_JUMP")

        base = 0x51 * 4
        self.micro_mem[base] = MicroInstruction(pc_write=1, cond="Z")
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x52 * 4
        self.micro_mem[base] = MicroInstruction(pc_write=1, cond="NZ")
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x53 * 4
        self.micro_mem[base] = MicroInstruction(pc_write=1, cond="G")
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x54 * 4
        self.micro_mem[base] = MicroInstruction(pc_write=1, cond="L")
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x55 * 4
        self.micro_mem[base] = MicroInstruction(pc_write=1, cond="GE")
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x55 * 4
        self.micro_mem[base] = MicroInstruction(pc_write=1, cond="C")
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x60 * 4
        self.micro_mem[base] = MicroInstruction(
            src_a="rd", use_imm=1, alu_op="SUB", reg_write=1
        )
        self.micro_mem[base + 1] = MicroInstruction(pc_write=1, cond="NZ")
        self.micro_mem[base + 2] = MicroInstruction(jump=1, next_addr=0)

        base = 0x70 * 4
        self.micro_mem[base] = MicroInstruction(sp_dec=1)
        self.micro_mem[base + 1] = MicroInstruction(
            mem_write=1, mem_addr="SP", mem_data="PC"
        )
        self.micro_mem[base + 2] = MicroInstruction(jump=1, next_addr=0)

        base = 0x71 * 4
        self.micro_mem[base] = MicroInstruction(mem_read=1, mem_addr="SP")
        self.micro_mem[base + 1] = MicroInstruction(reg_write=1, sp_inc=1)
        self.micro_mem[base + 2] = MicroInstruction(jump=1, next_addr=0)

        base = 0x72 * 4
        self.micro_mem[base] = MicroInstruction(
            mem_write=1, mem_addr="SP", mem_data="PC", sp_dec=1
        )
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr="IMM_JUMP")

        base = 0x73 * 4
        self.micro_mem[base] = MicroInstruction(
            mem_read=1, mem_addr="SP", reg_write=0, sp_inc=1
        )
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr="RET_PC")

        base = 0x74 * 4
        self.micro_mem[base] = MicroInstruction(jump=1, next_addr="PSTR")

        base = 0x75 * 4
        self.micro_mem[base] = MicroInstruction(mem_read=1, mem_addr="IN", reg_write=1)
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

        base = 0x76 * 4
        self.micro_mem[base] = MicroInstruction(mem_write=1, mem_addr="OUT")
        self.micro_mem[base + 1] = MicroInstruction(jump=1, next_addr=0)

    def step(self):
        if not self.halt:
            self.micro_step()

    def get_addr(self, name):
        if name == "r7":
            return self.SP

        if name == "imm":
            return self.IR & 0xFFF

        if name == "rd":
            return self.regs[(self.IR >> 20) & 0xF]

        if name == "rs1":
            return self.regs[(self.IR >> 16) & 0xF]

        if name == "rs2":
            return self.regs[(self.IR >> 12) & 0xF]

        if name == "SP":
            return self.SP

        if name == "IN":
            return self.IN

        return 0

    def get_src(self, name):
        if name == "rs1":
            return self.regs[(self.IR >> 16) & 0xF]
        if name == "rs2":
            return self.regs[(self.IR >> 12) & 0xF]
        if name == "rd":
            return self.regs[(self.IR >> 20) & 0xF]
        if name == "imm":
            return self.IR & 0xFFF
        if name == "r7":
            return self.SP
        if name == "PC":
            return self.PC

        return 0

    def micro_step(self):
        if self.MP == 0:
            self.IR = self.instr_mem.read(self.PC)
            self.micro_IR = self.IR
            self.MP = 1

        elif self.MP == 1:
            self.PC += 1
            self.MP = 10

        elif self.MP == 10:
            opcode = (self.micro_IR >> 24) & 0xFF
            self.MP = opcode * 4
        else:
            micro = self.micro_mem[self.MP]
            if micro is None:
                self.MP = 0
                return

            if micro.next_addr == "HALT":
                self.halt = True
                self.MP = 0
                return

            if micro.next_addr == "PSTR":
                rd = (self.micro_IR >> 20) & 0xF
                addr = self.regs[rd]
                length = self.data_mem.read(addr)
                for i in range(length):
                    c = self.data_mem.read(addr + i + 1)
                    self.output_buffer.append(self.data_mem.read(addr + i + 1))
                self.MP = 0
                return

            if micro.next_addr == "IMM_JUMP":
                self.PC = self.micro_IR & 0xFFF
                self.MP = 0
                return

            if micro.next_addr == "RET_PC":
                addr = self.data_mem.read(self.SP)
                self.PC = self.PC = self.buffer_reg
                self.MP = 0
                return

            if self.MP // 4 == 0x60:
                a = self.get_src("rd")
                b = 1
            else:
                a = self.get_src(micro.src_a)
                opcode = (self.micro_IR >> 24) & 0xFF
                if (
                    opcode == 0x72
                    and micro.src_a == "r7"
                    and micro.alu_op in ("ADD", "SUB")
                ):
                    b = 1
                elif (
                    opcode == 0x73
                    and micro.src_a == "r7"
                    and micro.alu_op in ("ADD", "SUB")
                ):
                    b = 1
                else:
                    b = (
                        self.micro_IR & 0xFFF
                        if micro.use_imm
                        else self.get_src(micro.src_b)
                    )

            if micro.alu_op:
                a = self.get_src(micro.src_a)

                if (
                    opcode in (0x70, 0x71, 0x72, 0x73)
                    and micro.src_a == "r7"
                    and micro.alu_op in ("ADD", "SUB")
                ):
                    b = 1
                else:
                    b = (
                        self.micro_IR & 0xFFF
                        if micro.use_imm
                        else self.get_src(micro.src_b)
                    )
                self.buffer_reg = self.ALU(micro.alu_op, a, b)

                if micro.write_flags:
                    self.update_hardware_flags(micro.alu_op, a, b, self.buffer_reg)

            elif micro.src_a is not None and not micro.mem_read:
                self.buffer_reg = a

            if micro.mem_addr == "SP":
                addr = self.SP
            elif micro.mem_addr is not None:
                addr = self.get_addr(micro.mem_addr)
            else:
                addr = self.buffer_reg

            if micro.mem_read:
                opcode = (self.micro_IR >> 24) & 0xFF
                if opcode == 0x10:
                    rs1 = (self.micro_IR >> 16) & 0xF
                    if rs1 != 0:
                        addr = self.get_addr("rs1")
                    else:
                        addr = self.micro_IR & 0xFFF
                if addr == self.IN:
                    if self.input_buffer:
                        self.buffer_reg = self.input_buffer.pop(0)
                    else:
                        self.buffer_reg = 0
                else:
                    self.buffer_reg = self.data_mem.read(addr)

            if micro.reg_write:
                rd = (self.micro_IR >> 20) & 0xF

                if micro.src_a == "r7":
                    self.SP = self.buffer_reg
                elif rd != 0:
                    self.regs[rd] = self.buffer_reg

            if micro.sp_dec:
                if self.SP > 0:
                    self.SP -= 1
                else:
                    raise Exception("Stack underflow")

            if micro.sp_inc:
                if self.SP < len(self.data_mem.mem) - 1:
                    self.SP += 1
                else:
                    raise Exception("Stack overflow")

            if micro.mem_write:
                opcode = (self.micro_IR >> 24) & 0xFF
                rs2 = (self.micro_IR >> 12) & 0xF
                imm = self.micro_IR & 0xFFF

                if opcode == 0x12:
                    if rs2 != 0:
                        addr = self.regs[rs2]
                    else:
                        addr = imm
                elif micro.mem_addr == "SP":
                    addr = self.SP
                elif micro.mem_addr is not None:
                    addr = self.get_addr(micro.mem_addr)
                else:
                    addr = self.buffer_reg

                if micro.mem_data is not None:
                    val = self.get_src(micro.mem_data)
                else:
                    val = self.get_src("rs1")

                if addr == self.OUT:
                    self.output_buffer.append(val)
                else:
                    self.data_mem.write(addr, val)

            if micro.pc_write:
                cond_met = False
                z = self.regs.flags["Z"]
                n = self.regs.flags["N"]
                v = self.regs.flags["V"]
                c = self.regs.flags["C"]

                if micro.cond == "Z":
                    cond_met = z == 1
                if micro.cond == "NZ":
                    cond_met = z == 0

                if micro.cond == "L":
                    cond_met = n != v
                if micro.cond == "LE":
                    cond_met = z == 1 or n != v
                if micro.cond == "G":
                    cond_met = z == 0 and n == v
                if micro.cond == "GE":
                    cond_met = n == v
                if micro.cond == "C":
                    cond_met = c == 1

                if cond_met:
                    self.PC = self.micro_IR & 0xFFF
                    self.MP = 0
                    return

            if micro.jump:
                self.MP = micro.next_addr
            else:
                self.MP += 1

        self.tick += 1

    def ALU(self, op, a, b):
        a &= 0xFFFFFFFF
        b &= 0xFFFFFFFF
        carry = 0
        def bitwise_add(x, y):
            carry_out = 0
            while y != 0:
                carry_out = x & y
                x = x ^ y
                y = (carry_out << 1) & 0xFFFFFFFF

            carry = (carry_out >> 31) & 1
            return x & 0xFFFFFFFF, carry

        def bitwise_sub(x, y):
            not_y = y ^ 0xFFFFFFFF
            res, carry_out = bitwise_add(x, not_y + 1)
            return res, carry_out

        def bitwise_mul(x, y):
            res = 0
            while y > 0:
                if y & 1:
                    res, _ = bitwise_add(res, x)
                x = (x << 1) & 0xFFFFFFFF
                y >>= 1
            return res

        def bitwise_div(x, y):
            if y == 0:
                return 0xFFFFFFFF
            quotient = 0
            remainder = 0
            for i in range(31, -1, -1):
                remainder = (remainder << 1) | ((x >> i) & 1)
                if remainder >= y:
                    remainder, _ = bitwise_sub(remainder, y)
                    quotient |= 1 << i
            return quotient & 0xFFFFFFFF

        result = 0

        if op == "ADD":
            result, carry = bitwise_add(a, b)
        elif op == "SUB":
            result, carry = bitwise_sub(a, b)
        elif op == "MUL":
            result = bitwise_mul(a, b)
            carry = 0
        elif op == "DIV":
            result = bitwise_div(a, b)
        elif op == "AND":
            result = a & b
            carry = 0
        elif op == "OR":
            result = a | b
            carry = 0
        elif op == "XOR":
            result = a ^ b
            carry = 0
        elif op == "CMP":
            result, carry = bitwise_sub(a, b)
            self.regs.flags["Z"] = int(result == 0)
            self.regs.flags["N"] = (result >> 31) & 1
            self.regs.flags["V"] = 0
            self.regs.flags["C"] = carry
            return result

        self.regs.flags["Z"] = int(result == 0)
        self.regs.flags["N"] = (result >> 31) & 1
        self.regs.flags["C"] = carry
        return result

    def update_hardware_flags(self, op, a, b, res):
        self.regs.flags["Z"] = int(res == 0)
        self.regs.flags["N"] = (res >> 31) & 1
        if op == "ADD":
            self.regs.flags["V"] = int(((a ^ res) & (b ^ res)) >> 31) & 1
        elif op == "SUB":
            self.regs.flags["V"] = int(((a ^ b) & (a ^ res)) >> 31) & 1
