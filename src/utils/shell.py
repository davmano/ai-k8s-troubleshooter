from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    command: list[str]
    stdout: str
    stderr: str
    returncode: int

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class ShellError(RuntimeError):
    pass


def run_command(command: list[str], timeout: int = 60) -> CommandResult:
    logger.debug("Running command: %s", " ".join(command))
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise ShellError(f"Command not found: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise ShellError(f"Command timed out: {' '.join(command)}") from exc

    return CommandResult(
        command=command,
        stdout=completed.stdout.strip(),
        stderr=completed.stderr.strip(),
        returncode=completed.returncode,
    )
