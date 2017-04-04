# KYC_Updater
Pulls KYC changes from Salesforce and registers then in KYC registry smart contract

## Cloning
This repo has submodules, so use `--recursive` while clonning

## Configuration
* `ENDPOINT_URI` - uri of the ETH node
* `PRIVATE_KEY` - private key of KYC updater
* `SF_PASSWORD` - salesforce api password
* `SF_TOKEN`- salesforce api token

## Runing
* Set config variables in config.env
* ```docker-compose up```

## Tests
* `pip install -r requirements.txt`
* set env config variables
* `py.test`
