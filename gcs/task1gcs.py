import subprocess
import platform
import sys
from pathlib import Path

raise ValueError('Incomplete. Run receiver.py and viewer.py manually in seperate terminals')

python = sys.executable
system = platform.system()

processes_dir = Path("processes")

for script in processes_dir.glob("*.py"):
    script_path = script.resolve()

    if system == "Windows":
        subprocess.Popen([
            "cmd", "/k",
            f'"{python}" "{script_path}"'
        ])

    elif system == "Linux":  # Linux (GNOME Terminal)
        subprocess.Popen([
            "gnome-terminal", "--", "bash", "-c",
            f'"{python}" "{script_path}"; exec bash'
        ])
    else:
        print('Unsupported system/OS!')
        break