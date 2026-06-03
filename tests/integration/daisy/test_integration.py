import unittest

from pathlib import Path

from hvcc.compiler import compile_dataflow
from hvcc.generators.c2daisy.json2daisy import generate_header_from_name


# Grabbing the absolute path to test data
data_path = Path(Path(__file__).parent, 'data')


class TestIntegration(unittest.TestCase):

    def test_patch(self):
        self.maxDiff = None
        header, info = generate_header_from_name('patch')
        with open(Path(data_path, 'integration', 'expected_patch.h'), 'r') as file:
            self.assertEqual(header, file.read(), 'The output string should match "expected_patch.h" exactly')

    def test_patch_init(self):
        self.maxDiff = None
        header, info = generate_header_from_name('patch_init')
        with open(Path(data_path, 'integration', 'expected_patch_init.h'), 'r') as file:
            self.assertEqual(header, file.read(), 'The output string should match "expected_patch_init.h" exactly')

    def test_petal(self):
        self.maxDiff = None
        header, info = generate_header_from_name('petal')
        with open(Path(data_path, 'integration', 'expected_petal.h'), 'r') as file:
            self.assertEqual(header, file.read(), 'The output string should match "expected_petal.h" exactly')

    def test_petal_125b_sm(self):
        self.maxDiff = None
        header, info = generate_header_from_name('petal_125b_sm')
        with open(Path(data_path, 'integration', 'expected_petal_125b_sm.h'), 'r') as file:
            self.assertEqual(header, file.read(), 'The output string should match "expected_petal_125b_sm.h" exactly')

    def test_pod(self):
        self.maxDiff = None
        header, info = generate_header_from_name('pod')
        with open(Path(data_path, 'integration', 'expected_pod.h'), 'r') as file:
            self.assertEqual(header, file.read(), 'The output string should match "expected_pod.h" exactly')

    def test_field(self):
        self.maxDiff = None
        header, info = generate_header_from_name('field')
        with open(Path(data_path, 'integration', 'expected_field.h'), 'r') as file:
            self.assertEqual(header, file.read(), 'The output string should match "expected_field.h" exactly')


def test_empty_display(tmp_path: Path):
    pd_path = tmp_path / "empty_display.pd"
    pd_path.write_text("""#N canvas 827 239 734 565 12;""")

    out_path = tmp_path / Path("out_dir")

    meta_path = tmp_path / "meta.json"
    meta_path.write_text("""{"name": "empty_display", "daisy": {"board": "petal"}}""")

    result = compile_dataflow(
        in_path=pd_path,
        out_dir=out_path,
        patch_meta_file=meta_path,
        generators=["daisy"],
    )

    assert len(result.root['c2daisy'].notifs.warnings) == 0


def test_empty_display_process(tmp_path: Path):
    pd_path = tmp_path / "empty_display_process.pd"
    pd_path.write_text("""#N canvas 827 239 734 565 12;""")

    out_path = tmp_path / Path("out_dir")

    meta_path = tmp_path / "meta.json"
    meta_path.write_text("""{"name": "empty_display_process", "daisy": {"board": "field"}}""")

    result = compile_dataflow(
        in_path=pd_path,
        out_dir=out_path,
        patch_meta_file=meta_path,
        generators=["daisy"],
    )

    assert result.root['c2daisy'].notifs.warnings[0].message == \
        "Unable to load display code from field. Using fallback."
