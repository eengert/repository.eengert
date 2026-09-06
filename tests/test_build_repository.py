import importlib.util
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY_ROOT / "scripts" / "build_repository.py"
SPEC = importlib.util.spec_from_file_location("build_repository", SCRIPT)
BUILD_REPOSITORY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD_REPOSITORY)


class BuildRepositoryTests(unittest.TestCase):
    def make_repository(self, temporary_directory):
        repository = temporary_directory / "repository.eengert"
        repository.mkdir()
        (repository / "addon.xml").write_text(
            '<addon id="repository.eengert" version="1.0.0" name="Eengert Repository" />',
            encoding="utf-8",
        )
        return repository

    def make_addon(self, temporary_directory):
        addon = temporary_directory / "plugin.test"
        (addon / "resources").mkdir(parents=True)
        (addon / "addon.xml").write_text(
            '<addon id="plugin.test" version="1.0.0" name="Test Add-on" />',
            encoding="utf-8",
        )
        (addon / "resources" / "runtime.py").write_text("print('ok')\n", encoding="utf-8")
        (addon / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        (addon / "tests").mkdir()
        (addon / "tests" / "test_runtime.py").write_text("assert True\n", encoding="utf-8")
        (addon / "resources" / "fixture.xcf").write_bytes(b"development fixture")
        (addon / "resources" / "dummy.mp4").write_bytes(b"development fixture")
        return addon

    def run_builder(self, repository_root, source):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--source",
                str(source),
                "--version",
                "2.3.4",
                "--repository-root",
                str(repository_root),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    def assert_packaged_files(self, repository_root):
        package = repository_root / "omega" / "zips" / "plugin.test" / "plugin.test-2.3.4.zip"
        with zipfile.ZipFile(package) as archive:
            names = set(archive.namelist())
            self.assertIn("plugin.test/addon.xml", names)
            self.assertIn("plugin.test/resources/runtime.py", names)
            self.assertNotIn("plugin.test/.gitignore", names)
            self.assertNotIn("plugin.test/tests/test_runtime.py", names)
            self.assertNotIn("plugin.test/resources/fixture.xcf", names)
            self.assertNotIn("plugin.test/resources/dummy.mp4", names)
            addon_xml = archive.read("plugin.test/addon.xml").decode("utf-8")
            self.assertIn('version="2.3.4"', addon_xml)

    def test_directory_source_filters_development_files(self):
        with tempfile.TemporaryDirectory() as directory:
            temporary_directory = Path(directory)
            self.make_repository(temporary_directory)
            addon = self.make_addon(temporary_directory)
            self.run_builder(temporary_directory, addon)
            self.assert_packaged_files(temporary_directory)

    def test_zip_source_is_supported_and_filtered(self):
        with tempfile.TemporaryDirectory() as directory:
            temporary_directory = Path(directory)
            self.make_repository(temporary_directory)
            addon = self.make_addon(temporary_directory)
            source_zip = temporary_directory / "plugin.test-1.0.0.zip"
            with zipfile.ZipFile(source_zip, "w") as archive:
                for source_file in addon.rglob("*"):
                    if source_file.is_file():
                        archive.write(source_file, Path(addon.name) / source_file.relative_to(addon))
            self.run_builder(temporary_directory, source_zip)
            self.assert_packaged_files(temporary_directory)

    def test_zip_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            temporary_directory = Path(directory)
            source_zip = temporary_directory / "malicious.zip"
            with zipfile.ZipFile(source_zip, "w") as archive:
                archive.writestr("../outside.txt", "must not escape")
            with self.assertRaises(SystemExit):
                BUILD_REPOSITORY.extract_addon_zip(source_zip, temporary_directory / "extract")
            self.assertFalse((temporary_directory / "outside.txt").exists())

    def test_invalid_source_does_not_delete_existing_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            temporary_directory = Path(directory)
            self.make_repository(temporary_directory)
            sentinel = temporary_directory / "omega" / "zips" / "addons.xml"
            sentinel.parent.mkdir(parents=True)
            sentinel.write_text("existing artifact", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--source",
                    str(temporary_directory / "missing.zip"),
                    "--version",
                    "2.3.4",
                    "--repository-root",
                    str(temporary_directory),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "existing artifact")


if __name__ == "__main__":
    unittest.main()
