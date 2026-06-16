"""Tests for the command-line interface."""

from __future__ import annotations

import json

import pytest

from persona_factory.cli import main


def test_generate_card(capsys) -> None:
    rc = main(["generate", "--seed", "42", "--format", "card"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.startswith("# ")


def test_generate_prompt(capsys) -> None:
    rc = main(["generate", "--seed", "42", "--format", "prompt"])
    assert rc == 0
    assert "You are" in capsys.readouterr().out


def test_generate_json_with_overrides(capsys) -> None:
    rc = main(["generate", "--seed", "1", "--format", "json", "--set", "gender=female"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["identity"]["gender"] == "female"


def test_generate_is_reproducible(capsys) -> None:
    main(["generate", "--seed", "5", "--format", "json"])
    first = capsys.readouterr().out
    main(["generate", "--seed", "5", "--format", "json"])
    second = capsys.readouterr().out
    assert first == second


def test_pool_jsonl(capsys) -> None:
    rc = main(["pool", "--n", "5", "--seed", "1"])
    assert rc == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 5
    for line in lines:
        json.loads(line)


def test_pool_to_file(tmp_path, capsys) -> None:
    out = tmp_path / "people.jsonl"
    rc = main(["pool", "--n", "3", "--seed", "1", "--out", str(out)])
    assert rc == 0
    assert len(out.read_text().strip().splitlines()) == 3


def test_pool_with_distribution(capsys) -> None:
    rc = main(["pool", "--n", "100", "--seed", "1", "--dist", "gender=female:0.5,male:0.5"])
    assert rc == 0
    lines = capsys.readouterr().out.strip().splitlines()
    genders = [json.loads(line)["identity"]["gender"] for line in lines]
    assert genders.count("female") == 50
    assert genders.count("male") == 50


def test_pool_invalid_distribution() -> None:
    with pytest.raises(SystemExit):
        main(["pool", "--n", "5", "--dist", "no-equals-sign"])


def test_locales_command(capsys) -> None:
    assert main(["locales"]) == 0
    assert "en_US" in capsys.readouterr().out


def test_presets_command(capsys) -> None:
    assert main(["presets"]) == 0
    assert "minimal_identity" in capsys.readouterr().out


def test_schema_command(capsys) -> None:
    assert main(["schema"]) == 0
    schema = json.loads(capsys.readouterr().out)
    assert "properties" in schema


def test_generate_with_preset(capsys) -> None:
    rc = main(["generate", "--preset", "minimal_identity", "--seed", "1", "--format", "json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "physical" not in data


def test_invalid_override_format() -> None:
    with pytest.raises(SystemExit):
        main(["generate", "--set", "noequalssign"])
