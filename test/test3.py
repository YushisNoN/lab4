"""
LOAD    R0       # 10
LOAD    R1       # 11
SUB   R2 = R1-R0 # 1
JNZ     7
ADDI    R2 = R2 + 100
HLT
ADDI    R2 = R2 + 500
HLT
"""
#

from CPU import CPU

cpu =  CPU()
cpu.instr_mem.write(0, 0x1000000B)
cpu.instr_mem.write(1, 0x1010000A)
cpu.instr_mem.write(2, 0x21210010)

cpu.instr_mem.write(3, 0x52000006)
cpu.instr_mem.write(4, 0x24220064)
cpu.instr_mem.write(5, 0x01000000)

cpu.instr_mem.write(6, 0x242201F4)
cpu.instr_mem.write(7, 0x01000000)

while not cpu.halt:
    cpu.step()
print(cpu.regs.R, cpu.regs.flags)