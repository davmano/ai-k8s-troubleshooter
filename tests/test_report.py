from src.reports.markdown_report import generate_markdown_report


def test_generate_markdown_report(tmp_path) -> None:
    path = generate_markdown_report(
        report_dir=str(tmp_path),
        resource="pod-a",
        namespace="dev",
        status="CrashLoopBackOff",
        symptoms="CrashLoop",
        root_cause="Bad env var",
        evidence="describe output",
        recommended_fix="Fix config",
        commands_to_run="kubectl describe",
        additional_checks="none",
    )
    assert path.exists()
    content = path.read_text()
    assert "# Kubernetes Diagnosis Report" in content
