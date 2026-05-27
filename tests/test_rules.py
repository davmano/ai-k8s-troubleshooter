from src.analyzers.rules import detect_issues


def test_detect_crashloop_and_oomkilled() -> None:
    matches = detect_issues("CrashLoopBackOff", "", "OOMKilled")
    issues = {m.issue for m in matches}
    assert "CrashLoopBackOff" in issues
    assert "OOMKilled" in issues
