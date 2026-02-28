from typer.testing import CliRunner
from darkprompt.main import app

runner = CliRunner()

def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "DarkPrompt version" in result.stdout

def test_analyze():
    result = runner.invoke(app, ["analyze", "Hello world"])
    assert result.exit_code == 0
    assert "Analyzing prompt" in result.stdout
