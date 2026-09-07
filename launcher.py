import os
import sys
import subprocess
import importlib.util
from pathlib import Path
import time


# ============================================================
# CATALYST // BOOTLOADER
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
REQUIREMENTS = BASE_DIR / "requirements.txt"
MAIN_SCRIPT = BASE_DIR / "script.py"


# ============================================================
# TERMINAL UI
# ============================================================

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def typewrite(text, delay=0.008):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


def banner():
    print(r"""
 ██████╗ █████╗ ████████╗ █████╗ ██╗     ██╗   ██╗███████╗████████╗
██╔════╝██╔══██╗╚══██╔══╝██╔══██╗██║     ██║   ██║██╔════╝╚══██╔══╝
██║     ███████║   ██║   ███████║██║     ██║   ██║███████╗   ██║
██║     ██╔══██║   ██║   ██╔══██║██║     ██║   ██║╚════██║   ██║
╚██████╗██║  ██║   ██║   ██║  ██║███████╗╚██████╔╝███████║   ██║
 ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝   ╚═╝

                    CATALYST SYSTEM BOOTLOADER
                         BUILD 1.0.0
""")


def status(label, value):
    print(f"  [{value:<8}] {label}")


# ============================================================
# PYTHON ENVIRONMENT
# ============================================================

def check_python():
    version = sys.version_info

    if version.major < 3 or (version.major == 3 and version.minor < 10):
        status("Python 3.10+ required", "FAIL")
        return False

    status(
        f"Python {version.major}.{version.minor}.{version.micro}",
        "OK"
    )

    return True


# ============================================================
# REQUIREMENTS
# ============================================================

def parse_requirements():
    if not REQUIREMENTS.exists():
        return []

    packages = []

    for line in REQUIREMENTS.read_text().splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        if line.startswith("-"):
            continue

        # Remove version specifiers so we can test imports
        package = line

        for operator in ["==", ">=", "<=", "~=", "!=", ">", "<"]:
            if operator in package:
                package = package.split(operator)[0]

        packages.append(package.strip())

    return packages


def package_to_import(package):
    """
    Converts common PyPI package names into import names.
    """
    mapping = {
        "PySide6": "PySide6",
        "python-dotenv": "dotenv",
        "mistralai": "mistralai",
        "scikit-learn": "sklearn",
        "opencv-python": "cv2",
        "Pillow": "PIL",
    }

    return mapping.get(package, package.replace("-", "_"))


def missing_packages(packages):
    missing = []

    for package in packages:
        module = package_to_import(package)

        if importlib.util.find_spec(module) is None:
            missing.append(package)

    return missing


def install_requirements():
    print()

    if not REQUIREMENTS.exists():
        status("requirements.txt", "NONE")
        return True

    status("requirements.txt", "FOUND")

    packages = parse_requirements()

    if not packages:
        status("Python dependencies", "NONE")
        return True

    missing = missing_packages(packages)

    if not missing:
        status("Python dependencies", "READY")
        return True

    print()
    print("  Missing dependencies:")
    for package in missing:
        print(f"    > {package}")

    print()
    print("  Installing missing dependencies...")
    print()

    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        str(REQUIREMENTS)
    ]

    result = subprocess.run(command)

    if result.returncode != 0:
        status("Dependency installation", "FAIL")
        return False

    status("Dependency installation", "OK")

    return True


# ============================================================
# PROJECT CHECKS
# ============================================================

def check_project():
    print()

    if MAIN_SCRIPT.exists():
        status("main.py", "FOUND")
    else:
        status("main.py", "FAIL")
        print()
        print("  ERROR: main.py was not found.")
        return False

    plugins = BASE_DIR / "plugins"

    if plugins.exists():
        status("Plugin directory", "FOUND")
    else:
        status("Plugin directory", "NONE")

    tools = BASE_DIR / "tools"

    if tools.exists():
        status("Tools directory", "FOUND")
    else:
        status("Tools directory", "NONE")

    return True


# ============================================================
# LAUNCH
# ============================================================

def launch():
    print()
    typewrite("  CATALYST CORE INITIALIZED", 0.015)
    typewrite("  QPROCESS EXECUTION ENGINE READY", 0.015)
    typewrite("  LAUNCHING MAIN PROCESS...", 0.015)

    time.sleep(0.5)

    print()

    result = subprocess.run(
        [sys.executable, str(MAIN_SCRIPT)],
        cwd=BASE_DIR
    )

    return result.returncode


# ============================================================
# MAIN
# ============================================================

def main():
    clear()
    banner()

    print("  ---------------------------------------------")
    print("              SYSTEM DIAGNOSTICS")
    print("  ---------------------------------------------")
    print()

    if not check_python():
        input("\n  Press ENTER to exit...")
        sys.exit(1)

    if not install_requirements():
        input("\n  Press ENTER to exit...")
        sys.exit(1)

    if not check_project():
        input("\n  Press ENTER to exit...")
        sys.exit(1)

    print()
    print("  ---------------------------------------------")
    print("                  SYSTEM READY")
    print("  ---------------------------------------------")
    print()

    time.sleep(1)

    exit_code = launch()

    print()
    print(f"  CATALYST PROCESS EXITED [{exit_code}]")
    input("\n  Press ENTER to close...")


if __name__ == "__main__":
    main()