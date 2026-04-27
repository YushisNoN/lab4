class InstructionStep:
    def __call__(self, cpu, instr):
        raise NotImplementedError

class NOP(InstructionStep):
    def __call__(self, cpu, instr):
        pass

class HALT(InstructionStep):
    def __call__(self, cpu, instr):
        cpu.halt = True

class LOADI(InstructionStep):
    def __call__(self, cpu, instr):
        cpu.regs[instr.rd] = instr.imm

class ADD(InstructionStep):
    def __call__(self, cpu, instr):
        cpu.regs[instr.rd] = cpu.regs[instr.rs1] + cpu.regs[instr.rs2]

class ADDI(InstructionStep):
    def __call__(self, cpu, instr):
        cpu.regs[instr.rd] = cpu.regs[instr.rd] + instr.imm

class LOAD(InstructionStep):
    def __call__(self, cpu, instr):
        addr = cpu.regs[instr.rs1] + instr.imm
        cpu.regs[instr.rd] = cpu.data_mem.read(addr)

class STORE(InstructionStep):
    def __call__(self, cpu, instr):
        addr = cpu.regs[instr.rs1] + instr.imm
        cpu.data_mem.write(addr, cpu.regs[instr.rd])

class SUB(InstructionStep):
    def __call__(self, cpu, instr):
        cpu.regs[instr.rd] = cpu.regs[instr.rs1] - cpu.regs[instr.rs2]

class SUBI(InstructionStep):
    def __call__(self, cpu, instr):
        cpu.regs[instr.rd] = cpu.regs[instr.rd] - instr.imm

class MUL(InstructionStep):
    def __call__(self, cpu, instr):
        cpu.regs[instr.rd] = cpu.regs[instr.rs1] * cpu.regs[instr.rs2]

class DIV(InstructionStep):
    def __call__(self, cpu, instr):
        cpu.regs[instr.rd] = cpu.regs[instr.rs1] // cpu.regs[instr.rs2]

class AND(InstructionStep):
    def __call__(self, cpu, instr):
        cpu.regs[instr.rd] = cpu.regs[instr.rs1] & cpu.regs[instr.rs2]

class OR(InstructionStep):
    def __call__(self, cpu, instr):
        cpu.regs[instr.rd] = cpu.regs[instr.rs1] | cpu.regs[instr.rs2]

class XOR(InstructionStep):
    def __call__(self, cpu, instr):
        cpu.regs[instr.rd] = cpu.regs[instr.rs1] ^ cpu.regs[instr.rs2]

class JMP(InstructionStep):
    def __call__(self, cpu, instr):
        cpu.IP = instr.imm

class JZ(InstructionStep):
    def __call__(self, cpu, instr):
        if cpu.regs.flags["Z"]:
            cpu.IP = instr.imm

class JNZ(InstructionStep):
    def __call__(self, cpu, instr):
        if not cpu.regs.flags["Z"]:
            cpu.IP = instr.imm

class MOV(InstructionStep):
    def __call__(self, cpu, instr):
        cpu.regs[instr.rd] = cpu.regs[instr.rs1]

class CMP(InstructionStep):
    def __call__(self, cpu, instr):
        result = cpu.regs[instr.rs1] - cpu.regs[instr.rs2]
        cpu.regs.flags["Z"] = int(result == 0)
        cpu.regs.flags["X"] = int(result < 1)

class CALL(InstructionStep):
    def __call__(self, cpu, instr):
        pass

class INC(InstructionStep):
    def __call__(self, cpu, instr):
        pass

class DEC(InstructionStep):
    def __call__(self, cpu, instr):
        pass

class NEG(InstructionStep):
    def __call__(self, cpu, instr):
        pass

class NOT(InstructionStep):
    def __call__(self, cpu, instr):
        pass

class LOOP(InstructionStep):
    def __call__(self, cpu, instr):
        pass

# Логические сдвиги влево - вправо
class SLL(InstructionStep):
    def __call__(self, cpu, instr):
        pass

class SRL(InstructionStep):
    def __call__(self, cpu, instr):
        pass

# Арифметические сдвиги
class SRA(InstructionStep):
    def __call__(self, cpu, instr):
        pass

# под вопросом
class SLA(InstructionStep):
    def __call__(self, cpu, instr):
        pass
