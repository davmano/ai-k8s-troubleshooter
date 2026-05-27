from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def generate_markdown_report(
    report_dir: str,
    resource: str,
    namespace: str,
    status: str,
    symptoms: str,
    root_cause: str,
    evidence: str,
    recommended_fix: str,
    commands_to_run: str,
    additional_checks: str,
) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = Path(report_dir)
    path.mkdir(parents=True, exist_ok=True)
    file_path = path / f"{resource}-{timestamp}.md"

    content = f"""# Kubernetes Diagnosis Report

## Resource
{resource}

## Namespace
{namespace}

## Status
{status}

## Symptoms
{symptoms}

## Root Cause
{root_cause}

## Evidence
{evidence}

## Recommended Fix
{recommended_fix}

## Commands to Run
{commands_to_run}

## Additional Checks
{additional_checks}
"""
    file_path.write_text(content, encoding="utf-8")
    return file_path
