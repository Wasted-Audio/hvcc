import pytest
import subprocess
from pathlib import Path

class CTestRunner:
    def __init__(self, tmp_path, request):
        self.tmp_path = tmp_path
        self.root_dir = Path(request.config.rootdir)
        self.static_dir = self.root_dir / "hvcc" / "generators" / "ir2c" / "static"
        self.c_dir = Path(__file__).parent

    def run(self, test_file, dependencies=None):
        dependencies = dependencies or []
        output_bin = self.tmp_path / "test.bin"
        
        # 1. Compilation Stage
        # Force HV_SIMD_NONE for stability in unit tests
        cmd = ["gcc", "-g", "-DHV_SIMD_NONE=1"] 
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
        return CTestResult(exec_result.returncode == 0, exec_result.returncode, exec_result.stdout, exec_result.stderr, status)

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

@pytest.fixture
def c_test(tmp_path, request):
    return CTestRunner(tmp_path, request)
