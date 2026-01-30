import subprocess

class CleanupRunner:
    def __init__(self, script_path: str):
        self.script_path = script_path

    def clean(self, workspace: str) -> tuple[bool, str]:
        try:
            proc = subprocess.run(
                ["bash", self.script_path],
                cwd=workspace,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            return proc.returncode == 0, proc.stdout.decode() + proc.stderr.decode()
        except Exception as e:
            return False, str(e)
