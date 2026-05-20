import os
import shutil
import subprocess

def find_pandoc():
    """
    Search for pandoc executable in system PATH and common installation directories on Windows.
    Returns:
        tuple: (executable_path, version_string) or (None, None)
    """
    # 1. Search in PATH
    pandoc_path = shutil.which("pandoc")
    if pandoc_path:
        version = get_pandoc_version(pandoc_path)
        if version:
            return pandoc_path, version

    # 2. Check common Windows install paths
    possible_paths = [
        r"C:\Program Files\Pandoc\pandoc.exe",
        r"C:\Program Files (x86)\Pandoc\pandoc.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Pandoc\pandoc.exe"),
        os.path.join(os.environ.get("APPDATA", ""), r"Pandoc\pandoc.exe"),
    ]

    for path in possible_paths:
        if path and os.path.exists(path):
            version = get_pandoc_version(path)
            if version:
                return path, version

    return None, None

def get_pandoc_version(executable_path):
    """
    Run pandoc --version to get its version details.
    """
    try:
        # Use subprocess.run and hide window on Windows
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0 # SW_HIDE

        result = subprocess.run(
            [executable_path, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            startupinfo=startupinfo,
            timeout=2
        )
        if result.returncode == 0:
            # First line is usually "pandoc x.y.z..."
            lines = result.stdout.strip().split('\n')
            if lines:
                return lines[0].strip()
    except Exception:
        pass
    return None
