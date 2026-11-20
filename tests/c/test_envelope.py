import pytest


def test_hv_signal_envelope(c_test, simd):
    """Level, cadence and accumulation, compared against a scalar reference."""
    result = c_test.run(
        "test_HvSignalEnvelope.c",
        dependencies=["HvSignalEnvelope.c"],
        simd=simd,
    )
    assert result.passed, str(result)


def test_hv_signal_envelope_bounds(c_test, simd, sanitizers_available):
    """Same test under ASan/UBSan, to catch out-of-bounds weight reads that
    only show up as a wrong dB value in a normal build."""
    if not sanitizers_available:
        pytest.skip("compiler cannot link ASan/UBSan here")
    result = c_test.run(
        "test_HvSignalEnvelope.c",
        dependencies=["HvSignalEnvelope.c"],
        simd=simd,
        sanitize=True,
    )
    assert result.passed, str(result)
