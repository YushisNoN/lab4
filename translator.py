import struct
import sys

import Opcodes


def translate(input, output="program.bin"):
    raw_lines = []
    labels = {}
    memory_map = {}
    str_map = {}
    current_pc = 0
    start_address = 0

    def parse_value(x):
        if x in labels:
            return labels[x]
        return int(x, 0)

    with open(input) as f:
        for line in f.readlines():
            raw_lines.append(line.split(";")[0].strip())
        lines = [li for li in raw_lines if li]
    PC = 0
    code_lines = []
    for line in lines:
        parts = line.replace(",", " ").split()

        if ":" in parts[0]:
            label = parts[0].replace(":", "")
            labels[label] = current_pc
            parts.pop(0)

        if not parts:
            continue

        first_word = parts[0].lower()

        if first_word == ".word":
            memory_map[current_pc] = ("DATA", parse_value(parts[1]))
            current_pc += 1
        elif first_word == ".str":
            text = line.split('"')[1]
            str_addr = current_pc

            if ":" in parts[0]:
                labels[parts[0].replace(":", "")] = str_addr

            memory_map[current_pc] = ("DATA", len(text) - 1)
            current_pc += 1

            for ch in range(len(text)):
                if text[ch] != "\\":
                    memory_map[current_pc] = ("DATA", ord(text[ch]))
                elif ch + 1 < len(text) and text[ch] == "\\" and text[ch + 1] == "n":
                    memory_map[current_pc] = ("DATA", 10)

                current_pc += 1

        elif first_word == ".org":
            current_pc = int(parts[1], 0)
        elif first_word == ".start":
            start_label = parts[1]
        elif line.endswith(":"):
            label = line[:-1]
            labels[label] = current_pc
        else:
            memory_map[current_pc] = ("CODE", " ".join(parts))
            current_pc += 1

    if "start_label" in locals():
        if start_label in labels:
            start_address = labels[start_label]
        else:
            print(f"Error: Start label '{start_label}' not found!")
            sys.exit(1)
    bin_result = []
    debug_info = []
    max_addr = max(memory_map.keys()) if memory_map else 0

    encoded_memory = {}
    debug_info = []

    SECTION_CODE = 0
    SECTION_DATA = 1

    for pc_addr in sorted(memory_map.keys()):
        line = memory_map[pc_addr]
        instruction = 0

        if line[0] == "DATA":
            instruction = line[1] & 0xFFFFFFFF
        elif line[0] == "CODE":
            parts = line[1].replace(",", " ").split()
            if not parts:
                continue

            mnemonic = parts[0].upper()
            if mnemonic == ".WORD":
                instruction = int(parts[1], 0) & 0xFFFFFFFF
            else:
                opcode = Opcodes.OPCODES[mnemonic]
                rd = rs1 = rs2 = imm = 0

                if mnemonic in ["JZ", "JNZ", "JL", "JG", "JGE", "JMP", "JC"]:
                    imm = labels[parts[1]]
                elif mnemonic == "LOOP":
                    rd = int(parts[1][1:])
                    imm = labels[parts[2]]
                elif mnemonic == "LOAD":
                    rd = int(parts[1][1:])
                    arg2 = parts[2]

                    if arg2.startswith("[") and arg2.endswith("]"):
                        reg = int(arg2[2:-1])
                        rs1 = reg
                    elif arg2 in labels:
                        imm = labels[arg2]
                    elif arg2.startswith("R"):
                        rs1 = int(arg2[1:])
                    else:
                        imm = parse_value(arg2)
                elif mnemonic == "LOADI":
                    if parts[2] in str_map:
                        imm = str_map[parts[2]]
                    else:
                        imm = parse_value(parts[2])
                    rd = int(parts[1][1:])
                elif mnemonic == "STORE":
                    rs1 = int(parts[1][1:])
                    arg2 = parts[2]
                    if arg2.startswith("[") and arg2.endswith("]"):
                        rs2 = int(arg2[2:-1])
                        imm = 0
                    elif arg2 in Opcodes.PORTS:
                        imm = Opcodes.PORTS[arg2]
                    elif arg2 in labels:
                        imm = labels[arg2]
                    elif arg2.startswith("R"):
                        rs2 = int(arg2[1:])
                    else:
                        imm = parse_value(arg2)
                elif mnemonic in ["ADD", "SUB", "MUL", "DIV"]:
                    rd = int(parts[1][1:])
                    rs1 = int(parts[2][1:])
                    rs2 = int(parts[3][1:])
                elif mnemonic == "NEG":
                    rd = int(parts[1][1:])
                    rs1 = 0
                    rs2 = int(parts[2][1:])
                    opcode = 0x21
                elif mnemonic in ["AND", "OR", "XOR"]:
                    rd = int(parts[1][1:])
                    rs1 = int(parts[2][1:])
                    rs2 = int(parts[3][1:])
                elif mnemonic == "PUSH":
                    rs1 = int(parts[1][1:])
                elif mnemonic == "POP":
                    rd = int(parts[1][1:])
                elif mnemonic == "PSTR":
                    rd = int(parts[1][1:])
                elif mnemonic == "CALL":
                    imm = labels[parts[1]]
                elif mnemonic == "RET":
                    pass
                elif mnemonic in ["MOV"]:
                    rd = int(parts[1][1:])
                    rs1 = int(parts[2][1:])
                elif mnemonic in ["CMP"]:
                    rs1 = int(parts[1][1:])
                    rs2 = int(parts[2][1:])
                elif mnemonic == "IN":
                    rd = int(parts[1][1:])
                elif mnemonic in ["ADDI", "SUBI"]:
                    rd = int(parts[1][1:])
                    if len(parts) == 3:
                        rs1 = rd
                        imm = parse_value(parts[2])
                    else:
                        rs1 = int(parts[2][1:])
                        imm = parse_value(parts[3])
                instruction = (
                    (opcode << 24) | (rd << 20) | (rs1 << 16) | (rs2 << 12) | (imm & 0xFFF)
                )

        encoded_memory[pc_addr] = (line[0], instruction)
        debug_info.append(f"{pc_addr:02X} - {instruction:08X} - {line}")

    code_sections = []
    data_sections = []
    sections = []
    sorted_addresses = sorted(encoded_memory.keys())

    def add_to_section(sections, addr, word):
        if sections and sections[-1]["start_addr_end"] == addr - 1:
            sections[-1]["words"].append(word)
            sections[-1]["start_addr_end"] = addr
        else:
            sections.append({"start_addr": addr, "start_addr_end": addr, "words": [word]})

    for addr in sorted_addresses:
        kind, word = encoded_memory[addr]
        if kind == "CODE":
            add_to_section(code_sections, addr, word)
        else:
            add_to_section(data_sections, addr, word)

    with open(output, "wb") as f:
        f.write(struct.pack(">I", start_address))
        # CODE_SECTION
        f.write(struct.pack(">I", len(code_sections)))
        for sec in code_sections:
            f.write(struct.pack(">I", sec["start_addr"]))
            f.write(struct.pack(">I", len(sec["words"])))
            for word in sec["words"]:
                f.write(struct.pack(">I", word))
        # DATA_SECTION
        f.write(struct.pack(">I", len(data_sections)))
        for sec in data_sections:
            f.write(struct.pack(">I", sec["start_addr"]))
            f.write(struct.pack(">I", len(sec["words"])))
            for word in sec["words"]:
                f.write(struct.pack(">I", word))

    with open(output + "_deg.txt", "w") as f:
        f.write(f"ENTRY POINT: {start_address:02X}\n")
        for entry in debug_info:
            f.write(entry + "\n")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        translate(sys.argv[1])
    else:
        translate(sys.argv[1], sys.argv[2])
