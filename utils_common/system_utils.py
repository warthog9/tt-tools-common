# SPDX-FileCopyrightText: © 2023 Tenstorrent Inc.
# SPDX-License-Identifier: Apache-2.0

"""
This file contains common utilities used by all tt-tools.
"""
import psutil
import distro
import platform
from typing import Union


def get_size(size_bytes: int, suffix: str = "B") -> str:
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if size_bytes < factor:
            return f"{size_bytes:.2f} {unit}{suffix}"
        size_bytes /= factor
    return "N/A"


def get_driver_version() -> Union[str, None]:
    try:
        with open("/sys/module/tenstorrent/version", "r", encoding="utf-8") as f:
            driver = f.readline().rstrip()
    except Exception:
        driver = None

    return driver


def get_host_info() -> dict:
    """
        Reads and organizes host info
    Returns:
        dict: with host info
    """
    uname = platform.uname()
    svmem = psutil.virtual_memory()

    os: str = uname.system
    distro_name: str = distro.name(pretty=True)
    kernel: str = uname.release
    hostname: str = uname.node

    return {
        "OS": os,
        "Distro": distro_name,
        "Kernel": kernel,
        "Hostname": hostname,
        "Platform": uname.machine,
        "Python": platform.python_version(),
        "Memory": get_size(svmem.total),
        "Driver": "TTKMD " + get_driver_version(),
    }


def system_compatibility() -> dict:
    host_info = get_host_info()
    checklist = {}
    if host_info["OS"] == "Linux":
        if distro.id() == "ubuntu":
            distro_version = float(".".join(distro.version_parts()[:2]))
            print(distro_version)
            if distro_version >= 20.04:
                checklist["OS"] = (True, "Pass")
            else:
                checklist["OS"] = (False, "Fail, not Ubuntu 20.04+")
        else:
            checklist["OS"] = (False, "Fail, not Ubuntu 20.04+")
    else:
        checklist["OS"] = (False, "Fail, not Ubuntu 20.04+")

    if host_info["Driver"]:
        checklist["Driver"] = (True, "Pass")
    else:
        checklist["Driver"] = (False, "Fail, no driver")
    if psutil.virtual_memory().total >= 32 * 1e9:
        checklist["Memory"] = (True, "Pass")
    else:
        checklist["Memory"] = (False, "Fail, not 32GB+")
    print(checklist)
    return checklist