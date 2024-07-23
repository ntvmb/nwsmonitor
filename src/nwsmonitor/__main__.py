"""NWSMonitor main script."""

import datetime
import logging
import asyncio
from sys import exit
from tendo import singleton
from .nwsmonitor import bot


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(
        prog="nwsmonitor",
        description="Discord bot that relays NWS watches and warnings.",
        epilog="For issue reports contact @virtualnate on Discord",
    )
    parser.add_argument("-t", "--token", help="Bot token", default="")
    parser.add_argument("-l", "--log-file", help="Log to file", default="")
    parser.add_argument("-v", "--verbose", help="Be verbose", action="store_true")
    parser.add_argument("-c", "--config", help="Use config file", default="")
    args = parser.parse_args()
    log_params = {}

    if args.token:
        _token = args.token
    else:
        try:
            with open("TOKEN", "r") as f:
                _token = f.read().split()[0]  # split in case of any newlines or spaces
        except FileNotFoundError:
            pass

    if args.log_file:
        log_params["filename"] = args.log_file
        log_params["filemode"] = "a"

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
        _token = config["token"]
        if config.get("log_file") is not None:
            log_params["filename"] = config["log_file"]
            log_params["filemode"] = "a"
            logging.captureWarnings(True)
    if args.verbose:
        log_params["level"] = logging.DEBUG
    else:
        log_params["level"] = logging.INFO
    logging.basicConfig(
        format="%(asctime)s.%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        **log_params,
    )

    try:
        # Prevent more than one instance from running at once
        me = singleton.SingleInstance(flavor_id="nwsmonitor")
    except singleton.SingleInstanceException:
        exit("Another instance of the bot is already running!")

    try:
        bot.run(_token)
    except NameError:
        parser.print_help()
    return


if __name__ == "__main__":
    main()
