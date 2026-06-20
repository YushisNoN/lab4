from CPU import CPU
from main import apply_config, load_config, load_program


def test_cat():
    cfg = load_config("tests/hello_user_name/hello_user_name_config.json")

    cpu = CPU(
        instr_mem_size=cfg["instr_memory_size"],
        data_mem_size=cfg["data_memory_size"],
    )

    apply_config(cpu, cfg)
    load_program(cpu, "tests/hello_user_name/hello_user_name.bin")

    while not cpu.halt:
        cpu.step()

    result = "".join(chr(x) for x in cpu.output_buffer)
    assert result == "What is your name?\nHello, Matvei"
