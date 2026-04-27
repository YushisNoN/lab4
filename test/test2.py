"""
LOAD R0         # 10
LOAD R1         # 15
SUB R2=R0-R1    # 0
HLT

10 00 00 0A
10 10 00 0F -> 00010000 00010000 00000000 00001111
               00010101 00000000 00000000 00000000
               00100000 00110000 00010000 00000000
21 20 00 00


"""

from CPU import CPU

cpu = CPU()
cpu.instr_mem.write(0, 0x1000000A)
cpu.instr_mem.write(1, 0x1010000F)
cpu.instr_mem.write(2, 0x21301000)
cpu.instr_mem.write(3, 0x01000000)

while not cpu.halt:
    cpu.step()

print(cpu.regs.R)
