from CPU import CPU
from main import load_program, load_config, apply_config


def test_cat():
    cfg = load_config("tests/cat/cat_config.json")

    cpu = CPU(
        instr_mem_size=cfg["instr_memory_size"],
        data_mem_size=cfg["data_memory_size"],
    )

    apply_config(cpu, cfg)
    load_program(cpu, "tests/cat/cat.bin")

    while not cpu.halt:
        cpu.step()

    result = "".join(chr(x) for x in cpu.output_buffer)
    assert result == "hello world! Hello everyone\t I need more bullets"