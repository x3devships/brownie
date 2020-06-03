import json
from pathlib import Path

from brownie.project.main import TempProject


def test_project_from_json():
    with Path(__file__).parent.joinpath("input.json").open() as fp:
        input_json = json.load(fp)

    with Path(__file__).parent.joinpath("output.json").open() as fp:
        output_json = json.load(fp)

    project = TempProject.from_compiler_json("TestProject", input_json, output_json)

    assert hasattr(project, "Token")
    assert hasattr(project, "SafeMath")
