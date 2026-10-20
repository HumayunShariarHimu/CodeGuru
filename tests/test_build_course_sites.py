import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_course_sites import output_map, rewrite_link


class DirectoryLinkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "course"
        self.chapter = self.root / "chapter"
        self.empty = self.root / "empty"
        self.chapter.mkdir(parents=True)
        self.empty.mkdir()
        (self.root / "README.md").write_text("# Course\n", encoding="utf-8")
        (self.chapter / "README.md").write_text("# Chapter\n", encoding="utf-8")
        (self.chapter / "topic.md").write_text("# Topic\n", encoding="utf-8")
        self.source = self.chapter / "topic.md"
        self.mapping = output_map(
            self.root,
            [self.root / "README.md", self.chapter / "README.md", self.source],
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_current_directory_link_resolves_to_readme(self):
        result = rewrite_link(
            "./", self.source, self.root, Path("chapter/topic.html"), self.mapping, "/CodeGuru"
        )
        self.assertEqual(result, "./README.html")

    def test_parent_directory_link_resolves_to_course_index(self):
        result = rewrite_link(
            "../", self.source, self.root, Path("chapter/topic.html"), self.mapping, "/CodeGuru"
        )
        self.assertEqual(result, "../index.html")

    def test_query_and_fragment_are_preserved(self):
        result = rewrite_link(
            "./?view=full#overview",
            self.source,
            self.root,
            Path("chapter/topic.html"),
            self.mapping,
            "/CodeGuru",
        )
        self.assertEqual(result, "./README.html?view=full#overview")

    def test_directory_without_landing_page_is_left_unchanged(self):
        result = rewrite_link(
            "../empty/", self.source, self.root, Path("chapter/topic.html"), self.mapping, "/CodeGuru"
        )
        self.assertEqual(result, "../empty/")


if __name__ == "__main__":
    unittest.main()
