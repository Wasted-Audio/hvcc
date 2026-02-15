from hvcc.interpreters.pd2hv.PdParser import PdParser


def test_re_dollar():
    string = "12 $3 4 $56 7"
    result = PdParser.RE_DOLLAR.findall(string)

    assert result == ["3", "56"]


def test_re_width():
    string = "#X obj 172 79 t b b, f 22"
    result = PdParser.RE_WIDTH.sub("", string)

    assert result == "#X obj 172 79 t b b"


def test_re_space():
    string = r"some\ thing else"
    result = PdParser.RE_SPACE.split(string)

    assert result == ["some\\ thing", "else"]
