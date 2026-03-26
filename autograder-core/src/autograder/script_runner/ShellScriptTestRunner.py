from autograder.script_runner.TestRunner import TestRunner
from autograder.logging.Logger import Logger

import subprocess
import os
from typing import Optional, Union, List
import uuid
import shutil


class ShellScriptTestRunner(TestRunner):
    """
    Executes build and run scripts for C assignments.
    Supports global project-level scripts and per-test overrides.

    This version runs each test inside a transient systemd unit so that:
    - every process created by the test lives in one cgroup
    - TasksMax can cap total tasks/processes
    - stopping the unit kills the whole test cleanly
    """

    def __init__(
        self,
        logger: Logger,
        buildScript,
        fatalErrors: List[str],
        placeholderRegex: Optional[dict] = None,
        tasksMax: int = 3000,
        systemdRunBin: str = "systemd-run",
        systemctlBin: str = "systemctl",
        sudoBin: str = "sudo",
        useSudoForSystemd: bool = True,
    ):
        super().__init__(logger, buildScript, fatalErrors, placeholderRegex)
        self.component = "ShellScriptTestRunner"

        self.tasksMax = tasksMax
        self.systemdRunBin = systemdRunBin
        self.systemctlBin = systemctlBin
        self.sudoBin = sudoBin
        self.useSudoForSystemd = useSudoForSystemd

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _systemd_prefix(self) -> List[str]:
        """
        Prefix commands with sudo -n if requested.
        """
        if self.useSudoForSystemd:
            return [self.sudoBin, "-n"]
        return []

    def _require_systemd_tools(self) -> None:
        if shutil.which(self.systemdRunBin) is None:
            raise RuntimeError(f"'{self.systemdRunBin}' not found in PATH")
        if shutil.which(self.systemctlBin) is None:
            raise RuntimeError(f"'{self.systemctlBin}' not found in PATH")

    def _make_unit_name(self, testFolderPath: str) -> str:
        test_name = os.path.basename(os.path.normpath(testFolderPath)) or "test"
        safe_test_name = "".join(
            c if c.isalnum() or c in ("-", "_", ".") else "_"
            for c in test_name
        )
        return f"autograder-{safe_test_name}-{uuid.uuid4().hex[:8]}.service"

    def _start_test_unit(
        self,
        unit_name: str,
        script: str,
        studentSubmissionPath: str,
        args: List[str],
    ) -> subprocess.Popen:
        """
        Start the run script inside a transient systemd service unit.

        --pipe forwards stdout/stderr from the script back to this process.
        --wait keeps systemd-run attached until the command exits.
        --collect lets systemd garbage-collect the unit after it stops.
        """
        cmd = [
            *self._systemd_prefix(),
            self.systemdRunBin,
            "--quiet",
            "--wait",
            "--pipe",
            "--collect",
            f"--unit={unit_name}",
            "-p", f"TasksMax={self.tasksMax}",
            "-p", "KillMode=control-group",
            script,
            studentSubmissionPath,
            *args,
        ]

        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def _stop_test_unit(self, unit_name: str) -> None:
        """
        Stop the transient unit and kill all processes in its cgroup.
        """
        cmd = [
            *self._systemd_prefix(),
            self.systemctlBin,
            "stop",
            unit_name,
        ]
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    def _reset_failed_unit(self, unit_name: str) -> None:
        """
        Best-effort cleanup in case the transient unit remains in a failed state.
        """
        cmd = [
            *self._systemd_prefix(),
            self.systemctlBin,
            "reset-failed",
            unit_name,
        ]
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )


    def get_process_counts(self):
        result = subprocess.run(
            ["ps", "-u", "TestP3", "-o", "stat="],
            capture_output=True,
            text=True
        )

        zombie_count = 0
        regular_count = 0

        for stat in result.stdout.splitlines():
            stat = stat.strip()
            if not stat:
                continue

            if stat.startswith("Z"):
                zombie_count += 1
            else:
                regular_count += 1

        return zombie_count, regular_count
    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------
    def build(self, studentSubmissionPath: str, buildScriptOverride: Optional[str] = None):
        """
        Builds a student submission using the provided build script.
        If no build script is provided, it assumes build success.
        """
        script = buildScriptOverride or self.buildScript
        if not script:
            return True, "", ""

        try:
            result = subprocess.run(
                [script, studentSubmissionPath],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                text=True
            )

            output = result.stdout.strip()
            error = result.stderr.strip()

            self.detectFatalErrors([output, error])

            return result.returncode == 0, output, error

        except subprocess.SubprocessError as e:
            self.logger.error(self._log_template({
                "StudentSubmissionPath": studentSubmissionPath,
                "BuildScript": script,
                "Error": str(e)
            }))
            return False, None, str(e)
        except Exception as e:
            self.logger.error(self._log_template({
                "StudentSubmissionPath": studentSubmissionPath,
                "BuildScript": script,
                "Error": str(e)
            }))
            return False, None, str(e)

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------
    def run(
        self,
        studentSubmissionPath: str,
        testFolderPath: str,
        inputData: Optional[Union[str, List[str]]] = None,
        expectedOutputFile: Optional[str] = None,
        runScript: Optional[str] = None,
        timeout: int = 120
    ) -> dict:
        """
        Runs a single test on the student submission.
        inputData can be:
        - a string (will be split into arguments)
        - a list of strings
        - None (no input arguments)
        """
        script = runScript
        output = None
        error = None
        proc = None
        unit_name = None

        if not script:
            self.logger.error(self._log_template({
                "StudentSubmissionPath": studentSubmissionPath,
                "RunScript": "",
                "Error": "No run script provided"
            }))
            raise ValueError("No run script provided")

        if inputData is None:
            args = []
        elif isinstance(inputData, str):
            args = inputData.strip().split()
        else:
            args = inputData

        try:
            self._require_systemd_tools()
            unit_name = self._make_unit_name(testFolderPath)

            proc = self._start_test_unit(
                unit_name=unit_name,
                script=script,
                studentSubmissionPath=studentSubmissionPath,
                args=args,
            )

            try:
                stdout, stderr = proc.communicate(timeout=timeout)
            except subprocess.TimeoutExpired as e:
                self._stop_test_unit(unit_name)

                try:
                    stdout, stderr = proc.communicate(timeout=10)
                except subprocess.TimeoutExpired:
                    stdout = e.stdout or ""
                    stderr = e.stderr or ""

                output = self._to_text(stdout).strip()
                error = self._to_text(stderr).strip()

                self.logger.error(self._log_template({
                    "StudentSubmissionPath": studentSubmissionPath,
                    "RunScript": script,
                    "Error": "TimeoutExpired",
                    "output": output,
                    "error": error,
                    "SystemdUnit": unit_name
                }))

                raise SystemExit(
                    "Autograder terminated due to fatal error: Timeout: student code took too long"
                )

            output = self._to_text(stdout).strip()
            error = self._to_text(stderr).strip()

            self.detectFatalErrors([output, error])

            return self.generateTestResults(output, error, expectedOutputFile)

        except Exception as e:
            self.logger.error(self._log_template({
                "StudentSubmissionPath": studentSubmissionPath,
                "RunScript": script,
                "Error": str(e),
                "SystemdUnit": unit_name
            }))
            self.detectFatalErrors([str(e)])
            return {
                "passed": False,
                "output": "",
                "expected": "",
                "error": f"Unexpected error: {str(e)}",
                "similarity_report": []
            }

        finally:
            if unit_name is not None:
                self._stop_test_unit(unit_name)
                self._reset_failed_unit(unit_name)

            # print(f"Processes for user TestP3 after test: {self.get_process_counts()}")