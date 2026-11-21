"""Start the API and Vite development server together."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
processes = []
try:
    processes.append(subprocess.Popen([sys.executable, '-m', 'uvicorn', 'backend.app.main:app', '--host', '127.0.0.1', '--port', '18000'], cwd=ROOT))
    npm = 'npm.cmd' if os.name == 'nt' else 'npm'
    processes.append(subprocess.Popen([npm, 'run', 'dev'], cwd=ROOT / 'frontend'))
    while all(process.poll() is None for process in processes):
        try:
            processes[0].wait(timeout=0.5)
        except subprocess.TimeoutExpired:
            pass
except KeyboardInterrupt:
    pass
finally:
    for process in processes:
        if process.poll() is None:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            else:
                process.terminate()
    for process in processes:
        process.wait()
