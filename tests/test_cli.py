import sys
from pathlib import Path
import tempfile

# Ensure package import works when running tests from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from click.testing import CliRunner
from personal_budget.cli import cli


def test_cli_add_and_list(tmp_path):
    db_file = tmp_path / "cli_budget.db"
    runner = CliRunner()
    result = runner.invoke(cli, ["--db", str(db_file), "add", "--type", "income", "--amount", "50", "--category", "Gift", "--desc", "Birthday"])
    assert result.exit_code == 0
    assert "Added transaction" in result.output

    result2 = runner.invoke(cli, ["--db", str(db_file), "list"])  # default limit
    assert result2.exit_code == 0
    assert "Gift" in result2.output
