import pytest

@pytest.mark.parametrize("simd", ["NONE", "SSE", "AVX"])
def test_hv_signal_envelope(c_test, simd):
    result = c_test.run("test_HvSignalEnvelope.c", dependencies=["HvSignalEnvelope.c"], simd=simd)
    assert result.passed, str(result)
