import struct
import sys
from CPU import CPU



def load_program(cpu, binary_filename):
    try:
        with open(binary_filename, 'rb') as f:
            header = f.read(4)
            if not header:
                return
            cpu.PC = struct.unpack('>I', header)[0]
            print(f"Entry point (PC) set to: {cpu.PC}")

            section_count = 0
            while True:
                section_header = f.read(8)
                if not section_header:
                    break
                target_addr, count = struct.unpack('>II', section_header)
                print(f"Loading section {section_count}: address {target_addr}, words: {count}")

                for i in range(count):
                    word_chunk = f.read(4)
                    if not word_chunk:
                        break
                    word = struct.unpack('>I', word_chunk)[0]

                    cpu.instr_mem.write(target_addr + i, word)
                    cpu.data_mem.write(target_addr + i, word)

                section_count += 1

        print(f"Successfully loaded {section_count} sections.")

    except Exception as e:
        print(f"Load error: {e}")

def dump_stack(self, depth=20):
    sp = self.regs[7]
    print(f"\nSTACK (top at SP={sp})")

    for i in range(depth):
        addr = sp + i
        if addr >= len(self.data_mem.mem):
            break
        print(f"SP+{i:02} [{addr:04}] = {self.data_mem.read(addr)}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("ERror")
        exit(1)
    bin_file = sys.argv[1]
    data_file = sys.argv[2]
    isDebug = False
    if len(sys.argv) == 4:
        isDebug = sys.argv[3] == "1"
    cpu = CPU()
    load_program(cpu, bin_file)
    with open(data_file, 'r') as f:
        cpu.input_buffer = list(f.read())

    try:
        while not cpu.halt:
            cpu.step()
            sp = cpu.regs[7]
            if isDebug:
                print(f"TICK: {cpu.tick:4} | PC: {cpu.PC:2} | MP: {cpu.MP:3} | "
                      f"IR: {cpu.IR:08X} | R0: {cpu.regs[0]} | R1: {cpu.regs[1]} | R2: {cpu.regs[2]}"
                      f" | FLAGS: {cpu.regs.flags}"
                      f" | STACK: {cpu.data_mem.mem[sp:sp+5]}"
                      )
        print("Simulation finished (HALT).")
        print("PROGRAM OUTPUT:")
        for idx, value in enumerate(cpu.output_buffer):
            print(f"{idx:4} | {value}")

    except Exception as e:
        print(f"Runtime error: {e}")