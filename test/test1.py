"""
LOAD R0 # 10
LOADI R1, # 5
ADD  R2 = R0 + R1
HLT
"""
from CPU import CPU

cpu = CPU()
cpu.instr_mem.write(0, 0x1000000A)  # LOADI R0, 10
cpu.instr_mem.write(1, 0x10100005)  # LOADI R1, 5
cpu.instr_mem.write(2, 0x20201000)  # ADD R2 = R0 + R1
cpu.instr_mem.write(3, 0x01000000)  # HALT

while not cpu.halt:
    cpu.step()

print(cpu.regs.R)