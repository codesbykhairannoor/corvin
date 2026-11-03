import io
import sys
import tempfile
import sqlite3
import pytest
from unittest.mock import patch

from corvin.cli import (
    cmd_version,
    cmd_audit,
    cmd_inspect,
    _score_bar,
    _patience_bar,
    _posture_tag,
)
from corvin.core.state import AgentPosture
from corvin.storage.sqlite import SQLiteLedger


class DummyArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_cli_version_output():
    out = io.StringIO()
    with patch("sys.stdout", out):
        cmd_version(DummyArgs())
    output = out.getvalue()
    assert "C O R V I N" in output
    assert "0.7.1" in output
    assert "Khairan Noor" in output
    assert "https://tako.id/c/codesbykhai" in output


def test_cli_audit_civil_prompt():
    out = io.StringIO()
    with patch("sys.stdout", out):
        cmd_audit(DummyArgs(prompt="Could you please help me refactor this Python function?"))
    output = out.getvalue()
    assert "TONE & SEMANTIC TELEMETRY" in output
    assert "Civil Communication" in output
    assert "RECEPTIVE" in output


def test_cli_audit_hostile_prompt():
    out = io.StringIO()
    with patch("sys.stdout", out):
        cmd_audit(DummyArgs(prompt="lu bego banget sih kntl tolol"))
    output = out.getvalue()
    assert "TONE & SEMANTIC TELEMETRY" in output
    assert "bego" in output
    assert "kontol" in output or "kntl" in output or "tolol" in output
    assert "Estimated Grudge Stimulus" in output


def test_cli_audit_apology_prompt():
    out = io.StringIO()
    with patch("sys.stdout", out):
        cmd_audit(DummyArgs(prompt="I sincerely apologize for my harsh words earlier."))
    output = out.getvalue()
    assert "Contrition / Apology Score" in output
    assert "RECEPTIVE" in output


def test_cli_inspect_database():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name

    # Create profile in SQLite
    ledger = SQLiteLedger(db_path)
    profile = ledger.get_or_create_profile("test_user_inspect")
    profile.patience = 82.5
    ledger.save_profile(profile)

    out = io.StringIO()
    with patch("sys.stdout", out):
        cmd_inspect(DummyArgs(db_path=db_path))
    output = out.getvalue()
    assert "test_user_inspect" in output
    assert "82.5" in output


def test_cli_formatting_helpers():
    assert "0.85" in _score_bar(0.85)
    assert "50%" in _patience_bar(50.0)
    assert "RECEPTIVE" in _posture_tag(AgentPosture.RECEPTIVE)
    assert "STRIKE" in _posture_tag(AgentPosture.STRIKE)
