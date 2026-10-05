from pathlib import Path

from caferank.extract import extract_csv


def test_extract_local_file(tmp_path: Path) -> None:
    source = tmp_path / "input.csv"
    source.write_text("a,b\n1,2\n")
    raw, frame = extract_csv(url=None, file=source)
    assert raw == b"a,b\n1,2\n"
    assert frame.to_dict("records") == [{"a": 1, "b": 2}]

