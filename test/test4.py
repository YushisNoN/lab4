from CPU import CPU

cpu = CPU()
cpu.input_buffer = ["A", "B"]

# RS = 253, IN = 255

# 1. LOADI R1, 253 (Адрес RS)
cpu.instr_mem.write(0, 0x101000FD)
# 2. LOAD R2, (R1) -> Читаем статус. Если в буфере "A", R2=1, Z=0.
cpu.instr_mem.write(1, 0x11210000)
# 3. JZ 1 -> Если Z=1 (статус был 0), прыгаем на адрес 1 (назад к LOAD).
cpu.instr_mem.write(2, 0x51000001)
# 4. LOADI R3, 255 (Адрес IN)
cpu.instr_mem.write(3, 0x103000FF)
# 5. LOAD R4, (R3) -> Читаем 'A'
cpu.instr_mem.write(4, 0x11430000)
# 6. HALT
cpu.instr_mem.write(5, 0x01000000)

while not cpu.halt:
    cpu.step()

print(f"Read character code: {cpu.regs[4]} (Char: {chr(cpu.regs[4])})")