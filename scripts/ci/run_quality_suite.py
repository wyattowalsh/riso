import subprocess
import sys

def run_command(command, cwd=None):
    """Runs a command and exits if it fails."""
    try:
        subprocess.run(command, check=True, cwd=cwd)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"Command `{' '.join(command)}` failed.", file=sys.stderr)
        sys.exit(1)

def main():
    """Runs the quality suite."""
    print("Running Ruff...")
    run_command(["ruff", "check", "."])
    print("Running Mypy...")
    run_command(["mypy", "."])
    print("Running Pylint...")
    run_command(["pylint", "template", "scripts"])

if __name__ == "__main__":
    main()