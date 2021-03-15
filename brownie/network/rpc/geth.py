#!/usr/bin/python3

import sys
from subprocess import DEVNULL, PIPE
from typing import Dict, List, Optional

import psutil
from requests.exceptions import ConnectionError as RequestsConnectionError
from web3.middleware import geth_poa_middleware

from brownie.exceptions import RPCRequestError
from brownie.network.web3 import web3

CLI_FLAGS = {
    "port": "--port",
    "gas_limit": "--gasLimit",
    "accounts": "--accounts",
    "evm_version": "--hardfork",
    "fork": "--fork",
    "mnemonic": "--mnemonic",
    "account_keys_path": "--acctKeys",
    "block_time": "--blockTime",
    "default_balance": "--defaultBalanceEther",
    "time": "--time",
    "unlock": "--unlock",
    "network_id": "--networkId",
    "chain_id": "--chainId",
}

EVM_VERSIONS = ["byzantium", "constantinople", "petersburg", "istanbul"]
EVM_DEFAULT = "istanbul"


def launch(cmd: str, **kwargs: Dict) -> None:
    print(f"\nLaunching '{cmd}'...")
    out = DEVNULL if sys.platform == "win32" else PIPE

    return psutil.Popen([cmd], stdin=DEVNULL, stdout=out, stderr=out)


def on_connection() -> None:
    if geth_poa_middleware not in web3._custom_middleware:
        web3._custom_middleware.add(geth_poa_middleware)
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)


def _request(method: str, args: List) -> int:
    try:
        response = web3.provider.make_request(method, args)  # type: ignore
        if "result" in response:
            return response["result"]
    except (AttributeError, RequestsConnectionError):
        raise RPCRequestError("Web3 is not connected.")
    raise RPCRequestError(response["error"]["message"])


def sleep(seconds: int) -> None:
    raise NotImplementedError("Geth dev does not support time travel")


def mine(timestamp: Optional[int] = None) -> None:
    raise NotImplementedError("Geth dev does not support empty mining")


def snapshot() -> int:
    raise NotImplementedError("Geth dev does not support snapshots or rewinds")


def revert(snapshot_id: int) -> None:
    raise NotImplementedError("Geth dev does not support snapshots or rewinds")


def unlock_account(address: str) -> None:
    raise NotImplementedError("Geth dev does not support unlocking accounts")
