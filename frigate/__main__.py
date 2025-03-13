import argparse
import faulthandler
import signal
import sys
import threading

from pydantic import ValidationError
from ruamel.yaml.scanner import ScannerError

from frigate.app import FrigateApp
from frigate.config import FrigateConfig
from frigate.log import setup_logging

minimal_config = {
            "mqtt": {"enabled": "false"},
            "environment_vars": {
                "INVALID_CONFIG": "true",
            },
            "cameras": {
                "null": {
                    "ffmpeg": {
                        "inputs": [
                            {"path": "/dev/null"}
                        ]
                    }
                }
            },
        }

def main() -> None:
    faulthandler.enable()

    # Setup the logging thread
    setup_logging()

    threading.current_thread().name = "frigate"

    # Make sure we exit cleanly on SIGTERM.
    signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit())

    # Parse the cli arguments.
    parser = argparse.ArgumentParser(
        prog="Frigate",
        description="An NVR with realtime local object detection for IP cameras.",
    )
    parser.add_argument("--validate-config", action="store_true")
    args = parser.parse_args()

    # Load the configuration.
    try:
        config = FrigateConfig.load(install=True)
    except (ValidationError, ScannerError) as e:
        print("*************************************************************")
        print("*************************************************************")
        print("***    Your config file is not valid!                     ***")
        print("***    Please check the docs at                           ***")
        print("***    https://docs.frigate.video/configuration/          ***")
        print("*************************************************************")
        print("*************************************************************")
        print("***    Config Validation Errors                           ***")
        print("*************************************************************")
        if e.__class__ == ValidationError:
            for error in e.errors():
                location = ".".join(str(item) for item in error["loc"])
                print(f"{location}: {error['msg']}")
        else:
            print(f"Failed to parse config: {e}")

        print("*************************************************************")
        print("***    End Config Validation Errors                       ***")
        print("*************************************************************")       

        FrigateApp(FrigateConfig(**minimal_config)).start_config_editor()

    if args.validate_config:
        print("*************************************************************")
        print("*** Your config file is valid.                            ***")
        print("*************************************************************")
        sys.exit(0)

    # Run the main application.
    FrigateApp(config).start()


if __name__ == "__main__":
    main()
