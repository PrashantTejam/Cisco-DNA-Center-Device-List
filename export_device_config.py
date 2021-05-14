#!/usr/bin/env python3

import os
from datetime import datetime
from distutils.util import strtobool

import requests
from colorama import init
from requests.packages import urllib3
from termcolor import cprint

# Disable SSL warnings. Not needed in production environments with valid certificates
# (REMOVE if you are not sure of its purpose)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# use Colorama to make Termcolor work on Windows too
init(autoreset=True)

# Export device configs to text files
def export_device_config(token: str, ENV: dict):
    """Exports device configurations into text files

    Args:
        token (str): Authentication token
        ENV (dict): Environment variables

    Raises:
        SystemExit: HTTP Errors
    """

    # Today's date
    today = datetime.today().strftime("%Y-%m-%d")

    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    DEVICE_CONFIG_URL = "/dna/intent/api/v1/network-device/config"

    try:
        response = requests.get(
            f"{ENV['BASE_URL']}{DEVICE_CONFIG_URL}",
            headers=headers,
            data=None,
            verify=True if strtobool(ENV["SSL_CERTIFICATE"]) else False,
        )
        response.raise_for_status()
        cprint("export_device_config:", "magenta")
        cprint(
            "The request was successful. The result is contained in the response body.\n",
            "green",
        )

        device_configs = response.json()["response"]

        DIR = "configs"

        # Create configs directory if not created
        os.makedirs(DIR, exist_ok=True)

        CONFIGS_DIR = f'{DIR}/{ENV["DOMAIN"]}/{today}'
        os.makedirs(f"{CONFIGS_DIR}", exist_ok=True)

        for config in device_configs:
            cfg = config["runningConfig"].strip()
            config_id = config["id"]
            cfg_file_name = f"{config_id}_{today}.txt"
            # Create a config file
            with open(os.path.join(CONFIGS_DIR, cfg_file_name), "w") as config_file:
                config_file.write(cfg)
                cprint(
                    f"'{cfg_file_name}' config file is created successfully!",
                    "cyan",
                )

    except requests.exceptions.HTTPError as err:
        raise SystemExit(cprint(err, "red"))
