"""
Standalone executable builder — wraps Python scripts into single-file
executables using PyInstaller.

The output binary bundles the Python interpreter, the script, and all
imported dependencies into one portable executable that can run on
machines without Python installed.
"""

import os
import shutil
import subprocess
import sys
import tempfile


def build_standalone(script_path: str, output_path: str) -> str:
    """Wrap a Python script into a standalone executable.

    Args:
        script_path: Path to the Python script to bundle.
        output_path: Desired output path for the executable.

    Returns:
        Path to the generated executable.
    """
    script_path = os.path.abspath(script_path)
    output_path = os.path.abspath(output_path)
    output_dir = os.path.dirname(output_path)
    output_name = os.path.splitext(os.path.basename(output_path))[0]

    # Create temp directories for PyInstaller artifacts
    spec_dir = tempfile.mkdtemp(prefix="hb_spec_")
    build_dir = tempfile.mkdtemp(prefix="hb_build_")

    try:
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--distpath", output_dir,
            "--specpath", spec_dir,
            "--workpath", build_dir,
            "--name", output_name,
            "--noconfirm",
            script_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            raise RuntimeError(
                "PyInstaller failed:\n" + result.stderr
            )

        # PyInstaller places the binary at <distpath>/<name> (or <name>.exe on Windows)
        if sys.platform == "win32":
            exe_path = os.path.join(output_dir, output_name + ".exe")
        else:
            exe_path = os.path.join(output_dir, output_name)

        if not os.path.isfile(exe_path):
            # Try to find what was produced
            produced = os.listdir(output_dir)
            raise RuntimeError(
                "Expected executable not found at '" + exe_path +
                "'. Files in output dir: " + str(produced)
            )

        # If the user-specified path differs from the PyInstaller output, move it
        if exe_path != output_path:
            if os.path.isfile(output_path):
                os.remove(output_path)
            shutil.move(exe_path, output_path)

        return output_path

    finally:
        # Clean up temp build artifacts
        for d in [spec_dir, build_dir]:
            if os.path.isdir(d):
                shutil.rmtree(d, ignore_errors=True)

