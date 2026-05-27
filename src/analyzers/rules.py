from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuleMatch:
    issue: str
    cause: str
    fix: str
    evidence: str


RULES = {
    "CrashLoopBackOff": (
        "Container repeatedly crashes after startup.",
        "Check app startup errors, env vars, probes, and dependencies.",
    ),
    "ImagePullBackOff": (
        "Kubernetes cannot pull container image.",
        "Verify image name/tag, registry access, and imagePullSecrets.",
    ),
    "ErrImagePull": (
        "Image pull failed due to auth/image/tag issue.",
        "Validate image reference and registry credentials.",
    ),
    "Pending": (
        "Pod cannot be scheduled.",
        "Inspect node resources, taints/tolerations, and PVC bindings.",
    ),
    "OOMKilled": (
        "Container terminated due to memory exhaustion.",
        "Increase memory limits or optimize application memory usage.",
    ),
    "CreateContainerConfigError": (
        "Container config is invalid or missing dependencies.",
        "Check ConfigMaps/Secrets/env references and volume mounts.",
    ),
}


def detect_issues(describe_output: str, logs_output: str, events_output: str) -> list[RuleMatch]:
    combined = "\n".join([describe_output, logs_output, events_output])
    matches: list[RuleMatch] = []

    for pattern, (cause, fix) in RULES.items():
        if pattern in combined:
            matches.append(RuleMatch(issue=pattern, cause=cause, fix=fix, evidence=f"Found '{pattern}'"))

    return matches
