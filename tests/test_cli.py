from src.analyzers.rules import RuleMatch
from src.cli import _rule_summary


def test_rule_summary() -> None:
    matches = [
        RuleMatch("CrashLoopBackOff", "crash", "fix crash", "Found CrashLoopBackOff"),
        RuleMatch("OOMKilled", "oom", "fix oom", "Found OOMKilled"),
    ]
    summary, status, symptoms, root_cause, evidence, fix = _rule_summary(matches)
    assert "CrashLoopBackOff" in summary
    assert status == "CrashLoopBackOff, OOMKilled"
    assert symptoms == "CrashLoopBackOff; OOMKilled"
    assert "crash" in root_cause
    assert "Found OOMKilled" in evidence
    assert "fix crash" in fix
