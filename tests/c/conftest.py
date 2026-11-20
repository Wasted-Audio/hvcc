"""Helpers for compiling and running the C unit tests.

Each test is a small Unity binary that links the generator's static C sources
against the mocks in tests/c/mocks. The binary is built per (test file, SIMD
flavour) so parametrised runs never overwrite each other's executable.
"""

import platform
import shutil
import subprocess
from pathlib import Path

import pytest


SIMD_FLAGS = {
    "NONE": ["-DHV_SIMD_NONE=1"],
    "SSE": ["-DHV_SIMD_SSE=1", "-msse", "-msse2", "-msse3", "-msse4.1"],
    "AVX": ["-DHV_SIMD_AVX=1", "-mavx"],
    "NEON": ["-DHV_SIMD_NEON=1"],
}


def get_available_simd():
    """SIMD flavours this machine can actually build and run."""
    machine = platform.machine().lower()
    if machine in ("arm64", "aarch64") or machine.startswith("arm"):
        return ["NONE", "NEON"]
    return ["NONE", "SSE", "AVX"]


def pytest_generate_tests(metafunc):
    """Parameterise any test that asks for a `simd` argument."""
    if "simd" in metafunc.fixturenames:
        metafunc.parametrize("simd", get_available_simd())


class CTestResult:
    def __init__(self, passed: bool, status: str, exit_code: int, stdout: str, stderr: str, command: list[str]):
        self.passed = passed
        self.status = status
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.command = command

    def __str__(self) -> str:
        msg = f"Status: {self.status} (exit code: {self.exit_code})\n"
        msg += "Command:\n  " + " ".join(self.command) + "\n"
        if self.stdout:
            msg += f"--- STDOUT ---\n{self.stdout}\n"
        if self.stderr:
            msg += f"--- STDERR ---\n{self.stderr}\n"
        return msg


class CTestRunner:
    def __init__(self, tmp_path: Path, request: pytest.FixtureRequest):
        self.tmp_path = Path(tmp_path)
        self.root_dir = Path(request.config.rootdir)
        self.static_dir = self.root_dir / "hvcc" / "generators" / "ir2c" / "static"
        self.c_dir = Path(__file__).parent

    @property
    def unity_src(self):
        return self.c_dir / "unity" / "src"

    def run(
        self,
        test_file: str,
        dependencies: list[str] | None = None,
        simd: str = "NONE",
        sanitize: bool = False
    ) -> CTestResult:
        dependencies = dependencies or []
        stem = Path(test_file).stem
        output_bin = self.tmp_path / f"{stem}.{simd}.bin"

        cc = shutil.which("clang") or shutil.which("cc")
        if cc is None:
            pytest.skip("no C compiler available")

        if not (self.unity_src / "unity.c").exists():
            pytest.skip("tests/c/unity submodule is not initialised")

        cmd = [cc, "-g", "-O1", "-Wall", "-Wextra", "-Wno-unused-parameter"]
        cmd.extend(SIMD_FLAGS[simd])
        if sanitize:
            cmd.extend(["-fsanitize=address,undefined", "-fno-omit-frame-pointer"])

        cmd.extend(["-I", str(self.unity_src)])
        cmd.extend(["-I", str(self.c_dir / "mocks")])
        cmd.extend(["-I", str(self.static_dir)])

        cmd.append(str(self.unity_src / "unity.c"))
        cmd.append(str(self.c_dir / "mocks" / "HeavyMock.c"))
        cmd.append(str(self.c_dir / test_file))
        cmd.extend(str(self.static_dir / dep) for dep in dependencies)
        cmd.extend(["-o", str(output_bin), "-lm"])

        compiled = subprocess.run(cmd, capture_output=True, text=True)
        if compiled.returncode != 0:
            return CTestResult(False, "COMPILATION_FAILED", compiled.returncode,
                               compiled.stdout, compiled.stderr, cmd)

        executed = subprocess.run([str(output_bin)], capture_output=True, text=True)
        ok = executed.returncode == 0
        return CTestResult(ok, "PASSED" if ok else "EXECUTION_FAILED",
                           executed.returncode, executed.stdout, executed.stderr, cmd)


@pytest.fixture(scope="session")
def sanitizers_available(tmp_path_factory: pytest.TempPathFactory):
    """True if the compiler can link ASan/UBSan on this machine."""
    cc = shutil.which("clang") or shutil.which("cc")
    if cc is None:
        return False
    probe_dir = tmp_path_factory.mktemp("sanitizer-probe")
    src = probe_dir / "probe.c"
    src.write_text("int main(void) { return 0; }\n")
    try:
        probe = subprocess.run(
            [cc, "-fsanitize=address,undefined", str(src), "-o", str(probe_dir / "probe")],
            capture_output=True,
            text=True,
        )
    except OSError:
        return False
    return probe.returncode == 0


@pytest.fixture
def c_test(tmp_path: Path, request: pytest.FixtureRequest) -> CTestRunner:
    return CTestRunner(tmp_path, request)
