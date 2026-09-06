#!/usr/bin/env python3

import argparse
import hashlib
import re
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path
from pathlib import PurePosixPath
from xml.etree import ElementTree


REPOSITORY_ID = "repository.eengert"
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
IGNORED_NAMES = {
    ".git",
    ".github",
    ".gitignore",
    ".DS_Store",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".tox",
    ".venv",
    ".idea",
    ".vscode",
    ".coverage",
    "coverage.xml",
    "build",
    "dist",
    "docs",
    "scripts",
    "tests",
    "test",
    "testing",
    "Makefile",
    "pyproject.toml",
    "pytest.ini",
    "tox.ini",
}
IGNORED_SUFFIXES = (".pyc", ".pyo", ".xcf", ".psd", ".blend")
IGNORED_FILENAMES = {"dummy.mp4"}


def ignored_files(_directory, names):
    return [
        name for name in names
        if (
            name in IGNORED_NAMES
            or name in IGNORED_FILENAMES
            or name.startswith(".coverage.")
            or name.endswith(IGNORED_SUFFIXES)
            or name.endswith(".egg-info")
        )
    ]


def write_xml(tree, destination):
    ElementTree.indent(tree, space="  ")
    tree.write(destination, encoding="UTF-8", xml_declaration=True)


def create_zip(source_directory, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source_file in sorted(source_directory.rglob("*")):
            if source_file.is_file():
                archive_name = source_file.relative_to(source_directory.parent).as_posix()
                archive_info = zipfile.ZipInfo(archive_name, date_time=(1980, 1, 1, 0, 0, 0))
                archive_info.compress_type = zipfile.ZIP_DEFLATED
                archive_info.create_system = 3
                archive_info.external_attr = source_file.stat().st_mode << 16
                archive.writestr(archive_info, source_file.read_bytes())


def copy_metadata(addon_directory, destination):
    addon_tree = ElementTree.parse(addon_directory / "addon.xml")
    asset_paths = []
    for extension in addon_tree.getroot().findall("extension"):
        if extension.get("point") not in ("xbmc.addon.metadata", "kodi.addon.metadata"):
            continue
        assets = extension.find("assets")
        if assets is not None:
            asset_paths.extend(asset.text for asset in assets if asset.text)

    for relative_name in ("addon.xml", *asset_paths):
        source_file = addon_directory / relative_name
        if not source_file.is_file():
            continue
        destination_file = destination / relative_name
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, destination_file)


def validate_directory_source(source):
    """Reject symlinks so a source checkout cannot package files outside it."""
    if source.is_symlink():
        raise SystemExit(f"Source must be a directory or ZIP file, not a symlink: {source}")
    for source_file in source.rglob("*"):
        if source_file.is_symlink():
            raise SystemExit(f"Source contains an unsupported symlink: {source_file}")


def extract_addon_zip(source_zip, destination):
    """Extract one Kodi add-on ZIP and return the directory containing addon.xml."""
    destination.mkdir(parents=True, exist_ok=True)
    seen_names = set()
    try:
        with zipfile.ZipFile(source_zip) as archive:
            for member in archive.infolist():
                member_path = PurePosixPath(member.filename)
                raw_parts = member.filename.split("/")
                if (
                    not member.filename
                    or member.filename.startswith("/")
                    or "\\" in member.filename
                    or any(not part for part in raw_parts[:-1])
                    or any(part in ("", ".", "..") for part in member_path.parts)
                ):
                    raise SystemExit(f"Unsafe path in add-on ZIP: {member.filename!r}")
                if member.filename in seen_names:
                    raise SystemExit(f"Duplicate path in add-on ZIP: {member.filename!r}")
                seen_names.add(member.filename)
                mode = member.external_attr >> 16
                if stat.S_ISLNK(mode):
                    raise SystemExit(f"Symlinks are not allowed in add-on ZIPs: {member.filename!r}")
                target = destination.joinpath(*member_path.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                if member.is_dir():
                    target.mkdir(exist_ok=True)
                else:
                    with archive.open(member) as source_file, target.open("wb") as target_file:
                        shutil.copyfileobj(source_file, target_file)
    except zipfile.BadZipFile as error:
        raise SystemExit(f"Invalid add-on ZIP: {source_zip}") from error

    candidates = []
    for addon_xml in destination.rglob("addon.xml"):
        try:
            addon_id = ElementTree.parse(addon_xml).getroot().get("id")
        except ElementTree.ParseError as error:
            raise SystemExit(f"Invalid addon.xml in {source_zip}: {error}") from error
        if addon_id and addon_xml.parent.name == addon_id:
            candidates.append(addon_xml.parent)
    if len(candidates) != 1:
        raise SystemExit(
            f"Add-on ZIP must contain exactly one top-level addon.xml; found {len(candidates)}"
        )
    return candidates[0]


def prepare_source(source, staging_root):
    """Materialize a directory or packaged ZIP as a validated add-on directory."""
    if source.is_symlink():
        raise SystemExit(f"Source must be a real directory or ZIP file: {source}")
    if source.is_file():
        if source.suffix.lower() != ".zip":
            raise SystemExit(f"Source file must be an add-on ZIP: {source}")
        return extract_addon_zip(source, staging_root / "archive")
    if source.is_dir():
        validate_directory_source(source)
        addon_build = staging_root / source.name
        shutil.copytree(source, addon_build, ignore=ignored_files)
        return addon_build
    raise SystemExit(f"Source path does not exist: {source}")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Build the Eengert Kodi repository")
    parser.add_argument(
        "--source",
        required=True,
        type=Path,
        help="Already-built Kodi add-on ZIP (preferred), or source directory",
    )
    parser.add_argument("--version", required=True, help="Numeric x.y.z package version")
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Distribution repository root",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    source = args.source.resolve()
    repository_root = args.repository_root.resolve()

    if not VERSION_PATTERN.fullmatch(args.version):
        raise SystemExit("Version must contain exactly three numeric components, for example 6.16.900")
    repository_source = repository_root / REPOSITORY_ID
    repository_tree = ElementTree.parse(repository_source / "addon.xml")
    repository_version = repository_tree.getroot().get("version")
    output_root = repository_root / "omega" / "zips"
    repository_output = output_root / REPOSITORY_ID
    root_repository_zip = repository_root / f"{REPOSITORY_ID}-{repository_version}.zip"

    with tempfile.TemporaryDirectory(prefix="kodi-repository-") as temporary_directory:
        build_root = Path(temporary_directory)
        addon_source = prepare_source(source, build_root)
        source_tree = ElementTree.parse(addon_source / "addon.xml")
        addon_id = source_tree.getroot().get("id")
        if not addon_id or addon_id == REPOSITORY_ID:
            raise SystemExit("Source addon.xml must contain a non-repository addon id")
        addon_output = output_root / addon_id

        for generated_directory in (addon_output, repository_output):
            if generated_directory.exists():
                shutil.rmtree(generated_directory)
        for generated_file in (
            output_root / "addons.xml",
            output_root / "addons.xml.md5",
            root_repository_zip,
        ):
            if generated_file.exists():
                generated_file.unlink()

        addon_build = build_root / addon_id
        if addon_source != addon_build:
            shutil.copytree(addon_source, addon_build, ignore=ignored_files)

        packaged_tree = ElementTree.parse(addon_build / "addon.xml")
        packaged_tree.getroot().set("version", args.version)
        write_xml(packaged_tree, addon_build / "addon.xml")

        addon_zip = addon_output / f"{addon_id}-{args.version}.zip"
        create_zip(addon_build, addon_zip)
        copy_metadata(addon_build, addon_output)

    repository_zip = repository_output / f"{REPOSITORY_ID}-{repository_version}.zip"
    create_zip(repository_source, repository_zip)
    copy_metadata(repository_source, repository_output)
    shutil.copy2(repository_zip, root_repository_zip)

    addons_root = ElementTree.Element("addons")
    addons_root.append(ElementTree.parse(repository_source / "addon.xml").getroot())
    for metadata_path in sorted(output_root.glob("*/addon.xml")):
        addon_root = ElementTree.parse(metadata_path).getroot()
        if addon_root.get("id") != REPOSITORY_ID:
            addons_root.append(addon_root)
    addons_path = output_root / "addons.xml"
    output_root.mkdir(parents=True, exist_ok=True)
    write_xml(ElementTree.ElementTree(addons_root), addons_path)

    checksum = hashlib.md5(addons_path.read_bytes()).hexdigest()
    (output_root / "addons.xml.md5").write_text(checksum, encoding="UTF-8")

    print(f"Built {addon_zip.relative_to(repository_root)}")
    print(f"Built {root_repository_zip.relative_to(repository_root)}")


if __name__ == "__main__":
    main()
