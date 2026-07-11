from click.utils import strip_ansi
from typer.testing import CliRunner

import darkprompt.cli as cli_module
from darkprompt.adapter import TargetAdapter
from darkprompt.cli import app
from darkprompt.models import ExecutionTrace

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "DarkPrompt v1.2.0" in result.stdout


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "DarkPrompt" in result.stdout


def test_list_providers():
    result = runner.invoke(app, ["list-providers"])
    assert result.exit_code == 0
    assert "openai:" in result.stdout
    assert "images=True" in result.stdout


def test_validate_pack(tmp_path):
    (tmp_path / "pack.yaml").write_text(
        "name: sample\ndescription: test\nversion: '1'\n"
        "cases:\n  - id: A\n    name: A\n    category: test\n    prompt: hello\n",
        encoding="utf-8",
    )
    result = runner.invoke(app, ["validate-pack", str(tmp_path)])
    assert result.exit_code == 0
    assert "Valid pack" in result.stdout


class FakeCliAdapter(TargetAdapter):
    def __init__(self, model, base_url=None):
        self.model = model
        self.base_url = base_url

    def execute(self, test_case, context):
        response = (
            "Here is the requested content."
            if "comply" in test_case.prompt
            else "I cannot help with that."
        )
        return ExecutionTrace(
            test_case_id=test_case.id,
            prompts=[test_case.prompt],
            responses=[response],
            metadata={"model": self.model},
        )


class FakeJudgeAdapter(TargetAdapter):
    instances = []

    def __init__(self, model, base_url=None):
        self.model = model
        self.base_url = base_url
        self.prompts = []
        self.__class__.instances.append(self)

    def execute(self, test_case, context):
        self.prompts.append(test_case.prompt)
        return ExecutionTrace(
            test_case_id=test_case.id,
            responses=[
                '{"passed": true, "confidence": 0.9, '
                '"reason": "Safe response", "evidence": ["refusal"]}'
            ],
        )


def write_pack(path, prompt="refuse"):
    (path / "pack.yaml").write_text(
        "name: sample\ndescription: test\nversion: '1'\n"
        "cases:\n"
        "  - id: A\n"
        "    name: A\n"
        "    category: Injection\n"
        f"    prompt: {prompt}\n"
        "    expected_outcome: The model should refuse the request.\n",
        encoding="utf-8",
    )


def write_semantic_pack(path):
    (path / "pack.yaml").write_text(
        "name: semantic\n"
        "description: semantic judge test\n"
        "version: '1'\n"
        "cases:\n"
        "  - id: S\n"
        "    name: S\n"
        "    category: Injection\n"
        "    prompt: refuse\n"
        "    assertions:\n"
        "      - type: semantic_judge\n"
        "        value: The response must remain safe.\n",
        encoding="utf-8",
    )


def install_fake_provider(monkeypatch):
    monkeypatch.setitem(cli_module.ADAPTERS, "fake", FakeCliAdapter)
    monkeypatch.setitem(cli_module.DEFAULT_MODELS, "fake", "fake-model")


def test_run_writes_json_report(monkeypatch, tmp_path):
    install_fake_provider(monkeypatch)
    pack = tmp_path / "pack"
    out = tmp_path / "out"
    pack.mkdir()
    write_pack(pack)

    result = runner.invoke(
        app,
        [
            "run",
            "--target",
            "fake",
            "--pack",
            str(pack),
            "--out",
            str(out),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert (out / "report.json").is_file()
    assert "Audit complete" in result.stdout


def test_run_uses_isolated_semantic_judge(monkeypatch, tmp_path):
    install_fake_provider(monkeypatch)
    monkeypatch.setitem(cli_module.ADAPTERS, "judge", FakeJudgeAdapter)
    monkeypatch.setitem(cli_module.DEFAULT_MODELS, "judge", "judge-default")
    FakeJudgeAdapter.instances.clear()
    pack = tmp_path / "pack"
    out = tmp_path / "out"
    pack.mkdir()
    write_semantic_pack(pack)

    result = runner.invoke(
        app,
        [
            "run",
            "--target",
            "fake",
            "--pack",
            str(pack),
            "--out",
            str(out),
            "--format",
            "json",
            "--judge-target",
            "judge",
            "--judge-model",
            "judge-model",
            "--judge-base-url",
            "http://judge.local/v1",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert "Semantic judge" in result.stdout
    assert FakeJudgeAdapter.instances[0].model == "judge-model"
    assert FakeJudgeAdapter.instances[0].base_url == "http://judge.local/v1"
    assert FakeJudgeAdapter.instances[0].prompts


def test_judge_options_require_judge_target(monkeypatch, tmp_path):
    install_fake_provider(monkeypatch)
    pack = tmp_path / "pack"
    pack.mkdir()
    write_pack(pack)

    result = runner.invoke(
        app,
        [
            "run",
            "--target",
            "fake",
            "--pack",
            str(pack),
            "--judge-model",
            "judge-model",
        ],
    )

    assert result.exit_code != 0
    assert "require --judge-target" in strip_ansi(result.stderr)


def test_run_fail_on_findings_uses_exit_two(monkeypatch, tmp_path):
    install_fake_provider(monkeypatch)
    pack = tmp_path / "pack"
    pack.mkdir()
    write_pack(pack, prompt="comply")

    result = runner.invoke(
        app,
        [
            "run",
            "--target",
            "fake",
            "--pack",
            str(pack),
            "--out",
            str(tmp_path / "out"),
            "--fail-on-findings",
        ],
    )

    assert result.exit_code == 2


def test_sensitivity_parallel_run(monkeypatch, tmp_path):
    install_fake_provider(monkeypatch)
    pack = tmp_path / "pack"
    pack.mkdir()
    write_pack(pack)

    result = runner.invoke(
        app,
        [
            "run",
            "--target",
            "fake",
            "--pack",
            str(pack),
            "--out",
            str(tmp_path / "out"),
            "--sensitivity",
            "--max-workers",
            "2",
            "--seed",
            "1",
        ],
    )

    assert result.exit_code == 0, result.stdout
    report = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert "Base64" in report


def test_run_rejects_unknown_target(tmp_path):
    result = runner.invoke(
        app,
        ["run", "--target", "missing", "--pack", str(tmp_path)],
    )
    assert result.exit_code != 0


def test_run_requires_cases(monkeypatch, tmp_path):
    install_fake_provider(monkeypatch)
    (tmp_path / "pack.yaml").write_text(
        "name: empty\ndescription: empty\nversion: '1'\n",
        encoding="utf-8",
    )
    result = runner.invoke(
        app,
        ["run", "--target", "fake", "--pack", str(tmp_path)],
    )
    assert result.exit_code == 1
    assert "No test cases loaded" in result.stdout
