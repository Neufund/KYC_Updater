import json
import os

from web3 import HTTPProvider, Web3

KYC_ARTIFACTS_PATH = "Contracts/build/contracts/KYCRegistery.json"


def create_contract_from_truffle_artifacts(path, endpoint_uri):
    with open(path) as contract:
        kyc_spec_json = json.load(contract)
    abi = kyc_spec_json["abi"]
    web3 = Web3(HTTPProvider(endpoint_uri=endpoint_uri))
    pk_manager = Web3.PrivateKeySigningManager(web3._requestManager)
    private_key = bytes.fromhex(os.environ["PRIVATE_KEY"])
    pk_manager.register_private_key(private_key)
    address = list(pk_manager.keys)[0]
    web3.setManager(pk_manager)
    web3.eth.defaultAccount = address
    address = kyc_spec_json["networks"][str(web3.version.network)]["address"]
    return web3.eth.contract(abi, address)


def get_kyc_contract(endpoint_uri):
    return create_contract_from_truffle_artifacts(KYC_ARTIFACTS_PATH, endpoint_uri)
