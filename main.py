import logging
import os
import signal
import sys
import time
from datetime import datetime, timedelta

import pytz
from simple_salesforce import Salesforce

from kyc import get_kyc_contract

logging.basicConfig(level=logging.INFO)

SF_INSTANCE = "eu11.salesforce.com"
SF_USERNAME = "remco+salesforce-api@neufund.org"

REQUIRED_ENV_CONFIG_FIELDS = ["SF_PASSWORD", "SF_TOKEN", "PRIVATE_KEY"]

WEB3_ENDPOINT = os.environ["ENDPOINT_URI"]

CHECK_INTERVAL = 60

for key in REQUIRED_ENV_CONFIG_FIELDS:
    if key not in os.environ:
        raise EnvironmentError("Required env variable {} missing".format(key))

sf = Salesforce(
    instance=SF_INSTANCE,
    username=SF_USERNAME,
    password=os.environ["SF_PASSWORD"],
    security_token=os.environ["SF_TOKEN"]
)


def get_time():
    return datetime.now(pytz.UTC)


checked_to = get_time() - timedelta(days=10)


def run_update_step():
    global checked_to
    logging.info("Run update step")
    now = get_time()
    logging.info("Checking for updates from: {} to: {}".format(checked_to, now))
    updated_contracts = sf.Contact.updated(checked_to, now)["ids"]
    logging.info("Updated contacts:")
    logging.info(updated_contracts)
    on_updated(updated_contracts)
    checked_to = now


KYC_FIELDS = ["KYC_Identification__c",
              "KYC_Address__c",
              "KYC_Submitted__c",
              "KYC_Accepted__c",
              "KYC_Rejected__c",
              "KYC_Response__c",
              "KYC_Document__c"]


def on_KYC_rejected(address):
    logging.info("On KYC rejected")
    kyc = get_kyc_contract(WEB3_ENDPOINT)
    tx_hash = kyc.transact().reject(address)
    logging.info("KYC rejection submitted: {}", tx_hash)


def on_KYC_accepted(address):
    logging.info("On KYC accepted")
    kyc = get_kyc_contract(WEB3_ENDPOINT)
    tx_hash = kyc.transact().accept(address)
    logging.info("KYC acceptance submitted: {}", tx_hash)


def on_updated(client_ids):
    for client_id in client_ids:
        client = sf.Contact.get(client_id)
        logging.info("Client: ")
        logging.info(client)
        address = client["Ethereum_Address__c"]
        if not address:
            continue
        if client["KYC_Rejected__c"]:
            on_KYC_rejected(address)
        if client["KYC_Accepted__c"]:
            on_KYC_accepted(address)
        on_KYC_accepted(address)


def on_sigint(*_):
    sys.exit(0)


def start_pooling():
    logging.info("Start pooling")
    while True:
        run_update_step()
        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, on_sigint)
    start_pooling()
