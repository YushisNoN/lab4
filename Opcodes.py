
OPCODES = {
    "HALT": 0x01,
    "NOP": 0x00,
    "LOAD": 0x10,
    "LOADI": 0x11,
    "STORE": 0x12,
    "ADD": 0x20,
    "SUB": 0x21,
    "MUL": 0x22,
    "DIV": 0x23,
    "ADDI": 0x24,
    "SUBI": 0x25,
    "MOV": 0x30,
    "CMP": 0x31,
    "AND": 0x40,
    "OR": 0x41,
    "XOR": 0x42,
    "JMP": 0x50,
    "JZ": 0x51,
    "JNZ": 0x52,
    "JG": 0x53,
    "JL": 0x54,
    "JGE": 0x55,
    "LOOP": 0x60,
    "NEG": 0x02,
    "PUSH": 0x70,
    "POP": 0x71,
}

PORTS = {
    "RS": 253,
    "OUT": 254,
    "IN": 255
}