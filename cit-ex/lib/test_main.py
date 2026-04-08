import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import main as main_module


def test_main_uses_crossref_email(monkeypatch, tmp_path):
    epub_path = tmp_path / "dummy.epub"
    epub_path.write_text("dummy epub")
    captured = {}

    class DummyExtractor:
        def __init__(self, epub):
            self.epub = epub

        def exctract_cit(self, _class_name):
            return ["Citation text"]

    class DummyRefine:
        def __init__(self, unstructured_citation, doi=None, email=None):
            captured["unstructured_citation"] = unstructured_citation
            captured["doi"] = doi
            captured["email"] = email

        @staticmethod
        def find_doi_match(_citation):
            return "10.1234/example"

        def _is_valid_doi(self):
            return False

        def process_crossref_data(self):
            raise AssertionError("process_crossref_data should not be called")

        def get_citation(self):
            return {"citation": "ok"}

    class DummyBar:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def next(self):
            return None

        def finish(self):
            return None

    monkeypatch.setenv("CROSSREF_EMAIL", "citations@example.com")
    monkeypatch.setattr(main_module, "Extractor", DummyExtractor)
    monkeypatch.setattr(main_module, "Refine", DummyRefine)
    monkeypatch.setattr(main_module, "Bar", DummyBar)
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", str(epub_path), "-c", "biblio", "--dry-run"],
    )

    main_module.main()

    assert captured["unstructured_citation"] == "Citation text"
    assert captured["doi"] == "10.1234/example"
    assert captured["email"] == "citations@example.com"
