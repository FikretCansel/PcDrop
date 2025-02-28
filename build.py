import subprocess
import sys

def build_exe():
    try:
        subprocess.run(["pyinstaller", "app.spec"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while building executable: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
