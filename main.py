import struct
import sys
from CPU import CPU, Memory
import json



def load_program(cpu, binary_filename):
    try:
        with open(binary_filename, 'rb') as f:
            header = f.read(4)
            if not header:
                return
            cpu.PC = struct.unpack('>I', header)[0]
            print(f"Entry point (PC) set to: {cpu.PC}")

            num_code_sections = struct.unpack('>I', f.read(4))[0]
            print(f"Code sections: {num_code_sections}")
            for i in range(num_code_sections):
                target_addr, count = struct.unpack('>II', f.read(8))
                print(f"[CODE] section {i}: addr={target_addr}, words={count}")
                for j in range(count):
                    word = struct.unpack('>I', f.read(4))[0]
                    cpu.instr_mem.write(target_addr + j, word)
            num_data_sections = struct.unpack('>I', f.read(4))[0]
            print(f"Data sections: {num_data_sections}")
            for i in range(num_data_sections):
                target_addr, count = struct.unpack('>II', f.read(8))
                print(f"[DATA] section {i}: addr={target_addr}, words={count}")
                for j in range(count):
                    word = struct.unpack('>I', f.read(4))[0]
                    cpu.data_mem.write(target_addr + j, word)

        print(f"Successfully loaded program.")

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

def debug(cpu):
    sp = cpu.regs[7]
    regs_str = " | ".join(
        [f"R{i}: {cpu.regs[i]:<4} | " for i in range(7)]
    )

    print(
        f"TICK: {cpu.tick:4} | PC: {cpu.PC:4} | MP: {cpu.MP:4} | "
        f"IR: {cpu.IR:08X} | "
        f"{regs_str} | "
        f"FLAGS: {cpu.regs.flags} | "
        f"STACK: {cpu.data_mem.mem[sp:sp + 5]}"
    )

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def apply_config(cpu, cfg):
    cpu.PC = cfg.get("entry_point", 0)

    inp = cfg.get("input", [])
    if isinstance(inp, str):
        cpu.input_buffer = [ord(c) for c in inp]
    else:
        cpu.input_buffer = inp

    for k, v in cfg.get("data_image", {}).items():
        cpu.data_mem.write(int(k), v)

    for k, v in cfg.get("instr_image", {}).items():
        cpu.instr_mem.write(int(k), v)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py program.bin input.txt [--debug to see a debug info]")
        exit(1)

    bin_file = sys.argv[1]
    data_file = sys.argv[2]
    isDebug = "--debug" in sys.argv

    cfg = load_config(data_file)

    cpu = CPU(
        instr_mem_size=cfg.get("instr_memory_size", 256),
        data_mem_size=cfg.get("data_memory_size", 256)
    )
    apply_config(cpu, cfg)
    load_program(cpu, bin_file)

    try:
        while not cpu.halt:
            cpu.step()

            if isDebug:
                debug(cpu)

        print("Simulation finished (HALT).")
        print("PROGRAM OUTPUT:")
        for idx, value in enumerate(cpu.output_buffer):
            print(f"{idx:4} | {value}")

    except Exception as e:
        print(f"Runtime error: {e}")