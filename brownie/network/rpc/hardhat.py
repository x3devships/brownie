#!/usr/bin/python3

import sys
import warnings
from pathlib import Path
from subprocess import DEVNULL, PIPE
from typing import Dict, List, Optional

import psutil
from requests.exceptions import ConnectionError as RequestsConnectionError

from brownie.exceptions import InvalidArgumentWarning, RPCRequestError
from brownie.network.web3 import web3

CLI_FLAGS = {"port": "--port", "fork": "--fork", "fork_block": "--fork-block-number"}
IGNORED_SETTINGS = ["chain_id"]


def launch(cmd: str, **kwargs: Dict) -> None:
    """Launches the RPC client.

    Args:
        cmd: command string to execute as subprocess"""
    # if sys.platform == "win32" and not cmd.split(" ")[0].endswith(".cmd"):
    #     if " " in cmd:
    #         cmd = cmd.replace(" ", ".cmd ", 1)
    #     else:
    #         cmd += ".cmd"
    cmd_list = cmd.split(" ")
    for key, value in [(k, v) for k, v in kwargs.items() if v and k not in IGNORED_SETTINGS]:
        try:
            cmd_list.extend([CLI_FLAGS[key], str(value)])
        except KeyError:
            warnings.warn(
                f"Ignoring invalid commandline setting for hardhat: "
                f'"{key}" with value "{value}".',
                InvalidArgumentWarning,
            )
    print(f"\nLaunching '{' '.join(cmd_list)}'...")
    out = DEVNULL if sys.platform == "win32" else PIPE

    # required so hardhat considers the folder to be a hardhat project
    # once hardhat network releases, we should be able to remove
    hardhat_config = Path("hardhat.config.js")
    if not hardhat_config.exists():
        hardhat_config.touch()

    return psutil.Popen(cmd_list, stdin=DEVNULL, stdout=out, stderr=out)


def on_connection() -> None:
    gas_limit = web3.eth.getBlock("latest").gasLimit
    web3.provider.make_request("evm_setBlockGasLimit", [hex(gas_limit)])  # type: ignore


def _request(method: str, args: List) -> int:
    try:
        response = web3.provider.make_request(method, args)  # type: ignore
        if "result" in response:
            return response["result"]
    except (AttributeError, RequestsConnectionError):
        raise RPCRequestError("Web3 is not connected.")
    raise RPCRequestError(response["error"]["message"])


def sleep(seconds: int) -> int:
    return _request("evm_increaseTime", [seconds])


def mine(timestamp: Optional[int] = None) -> None:
    params = [timestamp] if timestamp else []
    _request("evm_mine", params)


def snapshot() -> int:
    return _request("evm_snapshot", [])


def revert(snapshot_id: int) -> None:
    _request("evm_revert", [snapshot_id])


def unlock_account(address: str) -> None:
    web3.provider.make_request("hardhat_impersonateAccount", [address])  # type: ignore
