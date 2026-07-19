import pytest
from conftest import get_available_simd


@pytest.mark.parametrize("simd", get_available_simd())
def test_hv_signal_envelope(c_test, simd):
    result = c_test.run("test_HvSignalEnvelope.c", dependencies=["HvSignalEnvelope.c"], simd=simd)
    assert result.passed, str(result)
