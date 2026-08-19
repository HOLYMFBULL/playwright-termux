import sys
import subprocess

from playwright._repo_version import __version__
from playwright._impl._driver import compute_driver_executable, get_driver_env


def main() -> None:
    if "--version" in sys.argv[1:]:
        print(__version__)
        return

    try:
        driver_executable, driver_cli = compute_driver_executable()
        completed_process = subprocess.run(
            [driver_executable, driver_cli, *sys.argv[1:]],
            env=get_driver_env(),
        )
        sys.exit(completed_process.returncode)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
