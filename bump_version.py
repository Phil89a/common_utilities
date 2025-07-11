import re
import sys
import subprocess
from pathlib import Path

INIT_FILE = Path("common_utilities/__init__.py")
VERSION_PATTERN = r'__version__\s*=\s*"(?P<version>\d+\.\d+\.\d+)"'


def get_current_version():
    content = INIT_FILE.read_text()
    match = re.search(VERSION_PATTERN, content)
    if not match:
        print("❌ Could not find version in __init__.py")
        sys.exit(1)
    return match.group("version")


def bump_version(version: str, part: str) -> str:
    major, minor, patch = map(int, version.split('.'))

    if part == "patch":
        patch += 1
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        print("❌ Unknown bump type. Use: patch, minor, or major.")
        sys.exit(1)

    return f"{major}.{minor}.{patch}"


def update_version_file(new_version: str):
    content = INIT_FILE.read_text()
    new_content = re.sub(VERSION_PATTERN, f'__version__ = "{new_version}"', content)
    INIT_FILE.write_text(new_content)


def run_release_script():
    try:
        subprocess.run(["bash", "release.sh"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during release: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("patch", "minor", "major"):
        print("Usage: python bump_version.py [patch|minor|major]")
        sys.exit(1)

    current_version = get_current_version()
    new_version = bump_version(current_version, sys.argv[1])
    update_version_file(new_version)
    print(f"✅ Version bumped: {current_version} → {new_version}")

    run_release_script()


if __name__ == "__main__":
    main()