import json
import logging
import os
import tempfile

import pytest

from runnable.control_unit import ControlUnit
from runnable.datapath import DataPath
from runnable.head import replace_escape_sequences
from translator import Translator


@pytest.mark.golden_test("golden/*_rowlang.yml")
def test_golden(golden, caplog):
    caplog.set_level(logging.DEBUG)

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdirname = ""
        source = os.path.join(tmpdirname, "source.rowlang")
        input_data = golden["input"]
        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["source_code"])

    translator = Translator()

    translator.read_file(source)

    json_str = translator.get_json()

    assert json_str.replace(" ", "").replace("\n", "") == (
        golden["translated"].replace(" ", "").replace("\n", "")
    )

    json_file = json.loads(json_str)
    input_data = replace_escape_sequences(list(input_data.strip() + chr(0)))
    data_path = DataPath(json_file.get("data", []), input_data)
    control_unit = ControlUnit(data_path, json_file.get("text", []))
    control_unit.exec()

    output = "".join(control_unit.datapath.test_get_buffer(2))
    assert output.replace(" ", "").replace("\n", "").replace("\x00", "") == (
        golden["output"].replace(" ", "").replace("\n", "").replace("\x00", "")
    )

    caplogtext = "".join(caplog.messages)
    if len(caplogtext) >= 124000:
        lines = caplogtext.splitlines()[:1000]
        assert "\n".join(lines).replace(" ", "").replace("\n", "") == "".join(
            golden["log"].splitlines()[:1000]
        ).replace(" ", "").replace("\n", "")
    else:
        assert caplog.text.replace(" ", "").replace("\n", "") == golden["log"].replace(
            " ", ""
        ).replace("\n", "")
