import platform
import subprocess
from pathlib import Path

import pytest


class CTestRunner:
    def __init__(self, tmp_path, request):
        self.tmp_path = tmp_path
        self.root_dir = Path(request.config.rootdir)
        self.static_dir = self.root_dir / "hvcc" / "generators" / "ir2c" / "static"
        self.c_dir = Path(__file__).parent

    def run(self, test_file, dependencies=None, simd="NONE"):
        dependencies = dependencies or []
        output_bin = self.tmp_path / f"test_{simd}.bin"

        # 1. Compilation Stage - Switching to Clang
        cmd = ["clang", "-g"]

        # SIMD Flags
        if simd == "AVX":
            cmd.extend(["-DHV_SIMD_AVX=1", "-mavx"])
        elif simd == "SSE":
            cmd.extend(["-DHV_SIMD_SSE=1", "-msse", "-msse2", "-msse3", "-msse4.1"])
        elif simd == "NEON":
            cmd.extend(["-DHV_SIMD_NEON=1"])
        else:
            cmd.append("-DHV_SIMD_NONE=1")

        cmd.extend(["-I", str(self.c_dir / "unity" / "src")])
        cmd.extend(["-I", str(self.c_dir / "mocks")])
        cmd.extend(["-I", str(self.static_dir)])

        # Source files
        cmd.append(str(self.c_dir / "unity" / "src" / "unity.c"))
        cmd.append(str(self.c_dir / "mocks" / "HeavyMock.c"))
        cmd.append(str(self.c_dir / test_file))

        for dep in dependencies:
            cmd.append(str(self.static_dir / dep))

        cmd.extend(["-o", str(output_bin), "-lm"])

        comp_result = subprocess.run(cmd, capture_output=True, text=True)
        if comp_result.returncode != 0:
            return CTestResult(False, comp_result.returncode, "", comp_result.stderr, "COMPILATION_FAILED")

        # 2. Execution Stage
        exec_result = subprocess.run([str(output_bin)], capture_output=True, text=True)

        status = "PASSED" if exec_result.returncode == 0 else "EXECUTION_FAILED"
        return CTestResult(
            exec_result.returncode == 0, exec_result.returncode, exec_result.stdout, exec_result.stderr, status)


class CTestResult:
    def __init__(self, passed, exit_code, stdout, stderr, status):
        self.passed = passed
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.status = status

    def __str__(self):
        msg = f"Status: {self.status} (Exit Code: {self.exit_code})\n"
        if self.stdout:
            msg += f"--- STDOUT ---\n{self.stdout}\n"
        if self.stderr:
            msg += f"--- STDERR ---\n{self.stderr}\n"
        return msg


def get_available_simd():
    machine = platform.machine().lower()
    if "arm" in machine or "aarch64" in machine:
        return ["NONE", "NEON"]
    else:
        return ["NONE", "SSE", "AVX"]


@pytest.fixture
def c_test(tmp_path, request):
    return CTestRunner(tmp_path, request)
