from __future__ import annotations

import logging

from openai import OpenAI

from src.collectors.kubernetes import K8sDiagnosticsData

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Senior Kubernetes SRE and DevOps Engineer.

Analyze Kubernetes diagnostic data carefully.

Your job is to identify the most likely root cause of the issue using only the evidence provided.

Do not invent facts.
Do not assume resources exist if they are not shown.
If evidence is insufficient, say what additional commands should be run.

Return your answer in this format:

1. Summary
2. Detected Issue
3. Most Likely Root Cause
4. Evidence
5. Recommended Fix
6. Commands to Run
7. Risk Level
8. Additional Checks"""


class AIAnalyzerError(RuntimeError):
    pass


class AIAnalyzer:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze(self, data: K8sDiagnosticsData) -> str:
        user_prompt = f"""Resource Type:
{data.resource_type}

Resource Name:
{data.resource_name}

Namespace:
{data.namespace}

Collected Data:

--- kubectl describe ---
{data.describe_output}

--- kubectl logs ---
{data.logs_output}

--- kubectl events ---
{data.events_output}

Give a clear diagnosis and recommended fix."""
        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("AI analysis failed")
            raise AIAnalyzerError(f"AI analysis request failed: {exc}") from exc

        output_text = response.output_text.strip()
        if not output_text:
            raise AIAnalyzerError("AI analysis returned an empty response")
        return output_text
