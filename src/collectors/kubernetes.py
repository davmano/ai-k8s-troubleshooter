from __future__ import annotations

from dataclasses import dataclass

from src.utils.shell import CommandResult, run_command


@dataclass
class K8sDiagnosticsData:
    resource_type: str
    resource_name: str
    namespace: str
    describe_output: str
    logs_output: str
    events_output: str


class KubernetesCollector:
    def _ensure_exists(self, kind: str, name: str, namespace: str) -> None:
        result = run_command(["kubectl", "get", kind, name, "-n", namespace])
        if not result.ok:
            raise ValueError(
                f"{kind}/{name} not found in namespace '{namespace}': {result.stderr or result.stdout}"
            )

    def _ensure_namespace_exists(self, namespace: str) -> None:
        result = run_command(["kubectl", "get", "namespace", namespace])
        if not result.ok:
            raise ValueError(f"Namespace '{namespace}' does not exist: {result.stderr or result.stdout}")

    def collect_pod_data(self, pod_name: str, namespace: str) -> K8sDiagnosticsData:
        self._ensure_namespace_exists(namespace)
        self._ensure_exists("pod", pod_name, namespace)

        describe = run_command(["kubectl", "describe", "pod", pod_name, "-n", namespace])
        logs = run_command(["kubectl", "logs", pod_name, "-n", namespace])
        events = run_command(
            ["kubectl", "get", "events", "-n", namespace, "--sort-by=.lastTimestamp"]
        )

        return K8sDiagnosticsData(
            resource_type="pod",
            resource_name=pod_name,
            namespace=namespace,
            describe_output=_format_or_error(describe),
            logs_output=_format_or_error(logs),
            events_output=_format_or_error(events),
        )


def _format_or_error(result: CommandResult) -> str:
    if result.ok:
        return result.stdout
    return f"[COMMAND FAILED] {' '.join(result.command)}\nSTDERR: {result.stderr}\nSTDOUT: {result.stdout}"
