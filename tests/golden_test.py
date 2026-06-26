import contextlib
import importlib
import io
import json
import os
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

TESTS_DIR = Path(__file__).resolve().parent
CASES = [
    p
    for p in TESTS_DIR.iterdir()
    if p.is_dir() and not p.name.startswith("__") and not p.name.startswith(".")
]


def normalize_asm(src: str) -> str:
    lines = []
    for line in src.replace("\r", "").split("\n"):
        line = line.expandtabs(4)
        line = line.rstrip()
        if line.strip() == "":
            continue
        lines.append(line)
    return "\n".join(lines)


def str_presenter(dumper, data):
    if "\n" in data:
        data = data.replace("\r", "")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(str, str_presenter, Dumper=yaml.SafeDumper)


def fresh_modules():
    import CPU
    import main
    import translator

    return (
        importlib.reload(translator),
        importlib.reload(CPU),
        importlib.reload(main),
    )


def read_raw_asm(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r", "")


def run_case(case_dir: Path):
    translator, CPU, main = fresh_modules()

    asm_file = next(p for p in case_dir.iterdir() if p.suffix == ".asm")
    cfg_file = next((p for p in case_dir.iterdir() if p.name.endswith("_config.json")), None)

    bin_file = case_dir / (asm_file.stem + ".bin")

    translator.translate(str(asm_file), str(bin_file))

    cfg = {}
    if cfg_file:
        cfg = json.loads(cfg_file.read_text(encoding="utf-8"))

    cpu = CPU.CPU(
        instr_mem_size=cfg.get("instr_memory_size", 256),
        data_mem_size=cfg.get("data_memory_size", 256),
    )

    main.apply_config(cpu, cfg)
    main.load_program(cpu, str(bin_file))

    buf = io.StringIO()

    with contextlib.redirect_stdout(buf):
        while not cpu.halt:
            cpu.step()

        print("OUTPUT_BUFFER:", cpu.output_buffer)
        try:
            print("ASCII:", "".join(chr(x) for x in cpu.output_buffer))
        except Exception:
            print("ASCII: <not ascii>")

        print("TRACE:")
        for t in cpu.trace_buffer:
            print(t)

        print("CYCLES:", cpu.tick)

        print("MEMORY_DUMP:")
        for i in range(min(len(cpu.data_mem.mem), 64)):
            print(i, cpu.data_mem.mem[i])

        print("STACK_DUMP:")
        print(cpu.stack if hasattr(cpu, "stack") else "<no stack>")

    return buf.getvalue(), read_raw_asm(asm_file)


def parse_output(raw: str):
    lines = [line.rstrip() for line in raw.splitlines() if line.strip()]

    result = {
        "output_buffer": [],
        "ascii": "",
        "trace": [],
        "cycles": 0,
        "memory": [],
        "stack": None,
    }

    mode = None

    for line in lines:
        if line.startswith("OUTPUT_BUFFER:"):
            result["output_buffer"] = eval(line.split(":", 1)[1].strip())

        elif line.startswith("ASCII:"):
            result["ascii"] = line.split(":", 1)[1].strip()

        elif line == "TRACE:":
            mode = "trace"
            continue

        elif line.startswith("CYCLES:"):
            result["cycles"] = int(line.split(":")[1].strip())

        elif line == "MEMORY_DUMP:":
            mode = "mem"
            continue

        elif line == "STACK_DUMP:":
            mode = "stack"
            continue

        else:
            if mode == "trace":
                result["trace"].append(line)
            elif mode == "mem":
                result["memory"].append(line)
            elif mode == "stack":
                result["stack"] = line

    return result


@pytest.mark.parametrize("case_dir", CASES, ids=lambda x: x.name)
def test_golden(case_dir: Path):
    golden_file = case_dir / "golden.yml"
    update = os.environ.get("UPDATE_GOLDEN") == "1"

    raw_out, asm_source = run_case(case_dir)
    asm_source = normalize_asm(asm_source)
    actual = parse_output(raw_out)

    data = {
        "in_source": asm_source,
        "out_log": {
            "output_buffer": actual["output_buffer"],
            "ascii": actual["ascii"],
        },
        "trace": actual["trace"],
        "cycles": actual["cycles"],
        "memory": actual["memory"],
        "stack": actual["stack"],
    }

    if not golden_file.exists() or update:
        with golden_file.open("w", encoding="utf-8") as f:
            yaml.safe_dump(
                data,
                f,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False,
                width=120,
            )
    expected = yaml.safe_load(golden_file.read_text(encoding="utf-8"))

    actual_log = data["out_log"]
    expected_log = expected["out_log"]

    actual_filtered = {
        "output_buffer": actual_log.get("output_buffer"),
        "ascii": actual_log.get("ascii"),
    }

    expected_filtered = {
        "output_buffer": expected_log.get("output_buffer"),
        "ascii": expected_log.get("ascii"),
    }

    assert actual_filtered == expected_filtered, (
        f"Mismatch in {case_dir.name}\n\n"
        f"ACTUAL:\n{actual_filtered}\n\n"
        f"EXPECTED:\n{expected_filtered}"
    )
