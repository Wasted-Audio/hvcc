from hvcc.core.hv2ir.HeavyLangObject import HeavyLangObject


def test_dpf_bpm_hash():
    name = "__hv_dpf_bpm"

    hash = HeavyLangObject.get_hash(name)
    assert hash == 0xDF8C2721


def test_diacritics_in_hash():
    name = "sómething"
    try:
        HeavyLangObject.get_hash(name)
    except Exception:
        assert False
