import subprocess
from typing import List


def get_devices() -> List[str]:
    dev_status = (
        subprocess.run(["bluetoothctl", "info"], stdout=subprocess.PIPE)
        .stdout.decode("utf-8")
        .split("\n")
    )

    connected_devices = []
    current_dev = ""

    for line in dev_status:
        try:
            k, v = line.strip().split(":", 1)
        except ValueError:
            continue

        if k == "Name":
            current_dev = v.strip()
        elif k == "Alias":
            current_dev = v.strip()
        elif k == "Connected":
            if v.strip() == "yes":
                connected_devices.append(current_dev)

    return connected_devices


def get_status() -> bool:
    ctrlr_status = (
        subprocess.run(["bluetoothctl", "show"], stdout=subprocess.PIPE)
        .stdout.decode("utf-8")
        .split("\n")
    )

    for line in ctrlr_status:
        try:
            k, v = line.strip().split(":", 1)
        except ValueError:
            continue

        if k == "Powered":
            return v.strip() != "no"

    return False
