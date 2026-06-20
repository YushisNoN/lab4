from CPU import CPU
from main import apply_config, load_config, load_program


def test_cat():
    cfg = load_config("tests/largest_palindrome/largest_palindrome_config.json")

    cpu = CPU(
        instr_mem_size=cfg["instr_memory_size"],
        data_mem_size=cfg["data_memory_size"],
    )

    apply_config(cpu, cfg)
    load_program(cpu, "tests/largest_palindrome/largest_palindrome.bin")

    while not cpu.halt:
        cpu.step()

    result = cpu.output_buffer
    assert result == [906609]
