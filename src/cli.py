from __future__ import annotations

import logging

import typer

from src.analyzers.ai_analyzer import AIAnalyzer, AIAnalyzerError
from src.analyzers.rules import RuleMatch, detect_issues
from src.collectors.kubernetes import KubernetesCollector
from src.config import settings
from src.reports.markdown_report import generate_markdown_report
from src.utils.formatter import console, print_section

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")

app = typer.Typer(help="AI-powered Kubernetes troubleshooting CLI")
diagnose_app = typer.Typer()
app.add_typer(diagnose_app, name="diagnose")


def _rule_summary(matches: list[RuleMatch]) -> tuple[str, str, str, str, str]:
    summary = "\n".join(f"- {m.issue}: {m.cause}\n  Fix: {m.fix}" for m in matches)
    status = ", ".join(m.issue for m in matches)
    symptoms = "; ".join(m.issue for m in matches)
    root_cause = " | ".join(m.cause for m in matches)
    evidence = "\n".join(m.evidence for m in matches)
    fix = "\n".join(m.fix for m in matches)
    return summary, status, symptoms, root_cause, evidence + "\n", fix


@diagnose_app.command("pod")
def diagnose_pod(
    pod_name: str,
    namespace: str = typer.Option(..., "-n", "--namespace"),
    ai: bool = typer.Option(False, "--ai", help="Enable AI analysis using OpenAI"),
) -> None:
    """Diagnose a Kubernetes pod issue."""
    collector = KubernetesCollector()
    try:
        data = collector.collect_pod_data(pod_name, namespace)
    except Exception as exc:  # noqa: BLE001
        console.print(f"[bold red]Collection failed:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    matches = detect_issues(data.describe_output, data.logs_output, data.events_output)
    if matches:
        summary, status, symptoms, root_cause, evidence, fix = _rule_summary(matches)
        print_section("Rule-based Findings", summary, style="yellow")
    else:
        print_section("Rule-based Findings", "No known patterns detected.", style="green")
        status = "Unknown"
        symptoms = "No direct signature detected"
        root_cause = "Insufficient rule-based evidence"
        evidence = "No known issue signatures found"
        fix = "Run deeper diagnostics"

    ai_output = "AI analysis skipped"
    if ai:
        if not settings.openai_api_key:
            console.print("[bold red]OPENAI_API_KEY is not set.[/bold red]")
            raise typer.Exit(code=1)
        analyzer = AIAnalyzer(settings.openai_api_key, settings.openai_model)
        try:
            ai_output = analyzer.analyze(data)
            print_section("AI Analysis", ai_output, style="magenta")
        except AIAnalyzerError as exc:
            console.print(f"[bold red]AI analysis failed:[/bold red] {exc}")
            ai_output = f"AI analysis failed: {exc}"

    report_path = generate_markdown_report(
        report_dir=settings.report_dir,
        resource=pod_name,
        namespace=namespace,
        status=status,
        symptoms=symptoms,
        root_cause=root_cause,
        evidence=evidence,
        recommended_fix=fix,
        commands_to_run=(
            f"kubectl describe pod {pod_name} -n {namespace}\n"
            f"kubectl logs {pod_name} -n {namespace}\n"
            f"kubectl get events -n {namespace} --sort-by=.lastTimestamp"
        ),
        additional_checks=ai_output,
    )
    console.print(f"[bold green]Report generated:[/bold green] {report_path}")


if __name__ == "__main__":
    app()
