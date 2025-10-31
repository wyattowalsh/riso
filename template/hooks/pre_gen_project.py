import shutil
import subprocess
import sys

def main():
    tools = ["ruff", "mypy", "pylint"]
    missing_tools = []

    for tool in tools:
        if not shutil.which(tool):
            missing_tools.append(tool)

    if missing_tools:
        print(f"Missing quality tools: {', '.join(missing_tools)}")
        print("Attempting to install with uv...")
        try:
            subprocess.run(["uv", "pip", "install"] + missing_tools, check=True)
            print("Installation successful.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Failed to install missing tools with uv.", file=sys.stderr)
            print("Please install the missing tools manually.", file=sys.stderr)
            sys.exit(1)

    print("All quality tools are available.")

if __name__ == "__main__":
    main()