import json
import struct
import sys
from typing import Any

from CPU import CPU


def load_program(cpu: CPU, binary_filename: str) -> None:
    try:
        with open(binary_filename, "rb") as f:
            header = f.read(4)
            if not header:
                return
            cpu.PC = struct.unpack(">I", header)[0]
            print(f"Entry point (PC) set to: {cpu.PC}")

            num_code_sections = struct.unpack(">I", f.read(4))[0]
            print(f"Code sections: {num_code_sections}")
            for i in range(num_code_sections):
                target_addr, count = struct.unpack(">II", f.read(8))
                print(f"[CODE] section {i}: addr={target_addr}, words={count}")
                for j in range(count):
                    word = struct.unpack(">I", f.read(4))[0]
                    cpu.instr_mem.write(target_addr + j, word)

            num_data_sections = struct.unpack(">I", f.read(4))[0]
            print(f"Data sections: {num_data_sections}")
            for i in range(num_data_sections):
                target_addr, count = struct.unpack(">II", f.read(8))
                print(f"[DATA] section {i}: addr={target_addr}, words={count}")
                for j in range(count):
                    word = struct.unpack(">I", f.read(4))[0]
                    cpu.data_mem.write(target_addr + j, word)

        print("Successfully loaded program.")

    except Exception as e:
        print(f"Load error: {e}")


def trace_log(cpu: CPU) -> None:
    opcode = (cpu.IR >> 24) & 0xFF
    f = open("log.txt", "a+")
    regs = " ".join([f"R{i}={cpu.regs[i]}" for i in range(8)])

    f.write(
        f"T={cpu.tick} | "
        f"PC={cpu.PC} | "
        f"MP={cpu.MP} | "
        f"IR={cpu.IR:08X} | "
        f"OP={opcode:02X} | "
        f"{regs} | "
        f"SP={cpu.SP} | "
        f"Z={cpu.regs.flags['Z']} "
        f"N={cpu.regs.flags['N']} "
        f"C={cpu.regs.flags['C']}\n"
    )
    f.close()


def debug(cpu: CPU, isMemory: bool = False, isStack: bool = False) -> None:
    regs_str = " | ".join([f"R{i}: {cpu.regs[i]:<4} | " for i in range(len(cpu.regs.R))])

    print(
        f"TICK: {cpu.tick:4} | PC: {cpu.PC:4} | MP: {cpu.MP:4} | "
        f"IR: {cpu.IR:08X} | "
        f"{regs_str} | "
        f"FLAGS: {cpu.regs.flags} | "
        f"SP: {cpu.SP:4} | "
    )

    if isStack:
        print(f"STACK: {cpu.data_mem.mem[cpu.SP - 5 :]}")

    if cfg.get("memory") is not None and isMemory:
        print(
            f"Memory[{cfg.get('memory')['start']:4}:{cfg.get('memory')['end']:4}]: ",
            cpu.data_mem.mem[cfg.get("memory")["start"] : cfg.get("memory")["end"]],
        )


def load_config(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def apply_config(cpu: CPU, cfg: dict[str, Any]) -> None:
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
    isMemoryDump = "--m" in sys.argv
    isStack = "--s" in sys.argv
    isTrace = "--t" in sys.argv
    cfg = load_config(data_file)

    cpu = CPU(
        instr_mem_size=cfg.get("instr_memory_size", 256),
        data_mem_size=cfg.get("data_memory_size", 256),
    )
    apply_config(cpu, cfg)
    load_program(cpu, bin_file)

    try:
        while not cpu.halt:
            cpu.step()

            if isDebug:
                debug(cpu, isMemoryDump, isStack)
            if isTrace:
                trace_log(cpu)

        print("Simulation finished (HALT).")
        cpu.dump_trace()
        print("PROGRAM OUTPUT:")
        for idx, value in enumerate(cpu.output_buffer):
            print(f"{idx:4} | {value}")
        print("\nPROGRAM OUTPUT (ascii):")
        try:
            output = ""
            for x in cpu.output_buffer:
                if isinstance(x, str):
                    print(x)
                else:
                    output += chr(x)
            print("".join(output))
        except UnicodeEncodeError:
            print("<not ascii>")
    except Exception as e:
        print(f"Runtime error: {e}")
