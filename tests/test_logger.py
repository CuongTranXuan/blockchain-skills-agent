import json
import tempfile
from pathlib import Path

from agent.logger import AgentLogger
from agent.types import TokenBalance


def test_logger_creates_file():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name

    log = AgentLogger("0xTEST", output_path=path)
    log.entry("discover", "read-portfolio", "skill-adapt.md", {"chain": "base"}, {"tokens": []})
    result = log.finalize()

    assert result["agent"] == "blockchain-skills-agent"
    assert result["erc8004"] == "0xTEST"
    assert len(result["entries"]) == 1
    assert result["entries"][0]["phase"] == "discover"
    assert "finishedAt" in result

    saved = json.loads(Path(path).read_text())
    assert len(saved["entries"]) == 1


def test_logger_incremental_ids():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name

    log = AgentLogger("0x", output_path=path)
    log.entry("p1", "a1", "s1")
    log.entry("p2", "a2", "s2")
    log.entry("p3", "a3", "s3")
    result = log.finalize()

    ids = [e["id"] for e in result["entries"]]
    assert ids == [1, 2, 3]


def test_logger_handles_dataclass_input():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name

    log = AgentLogger("0x", output_path=path)
    token = TokenBalance("ETH", "", 10**18, 18)
    log.entry("discover", "test", "s", input_data=token)
    result = log.finalize()

    assert result["entries"][0]["input"]["symbol"] == "ETH"


def test_logger_crash_safe_flush():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name

    log = AgentLogger("0x", output_path=path)
    log.entry("p", "a", "s")

    intermediate = json.loads(Path(path).read_text())
    assert len(intermediate["entries"]) == 1
    assert "finishedAt" not in intermediate
