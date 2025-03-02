import subprocess
import sys
import PyInstaller.__main__

def build_exe():
    try:
        PyInstaller.__main__.run([
            'run.py',
            '--name=PcDrop',
            '--onefile',
            '--windowed',
            '--add-data=static;static',
            '--add-data=templates;templates',
            '--icon=static/favicon.ico'
        ])
    except Exception as e:
        print(f"Error while building executable: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
