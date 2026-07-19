import pytest

def test_hv_signal_envelope_init(c_test):
    result = c_test.run("test_HvSignalEnvelope.c", dependencies=["HvSignalEnvelope.c"])
    assert result.passed, str(result)
