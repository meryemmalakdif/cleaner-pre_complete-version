import time
import click
# Get the path to the FederatedLearning directory relative to my_script.py
from FederatedLearning import smart_contract_functions
from FederatedLearning import utilities
from FederatedLearning import *


@click.command()
@click.option('--provider', default='http://127.0.0.1:8545', help='web3 API HTTP provider')
@click.option('--abi', default='./build/contracts/NoScore.json', help='contract abi file')
@click.option('--ipfs', default='/ip4/127.0.0.1/tcp/5001', help='IPFS api provider')
@click.option('--account', help='ethereum account to use for this computing server', required=True)
@click.option('--passphrase', help='passphrase to unlock account', required=True)
@click.option('--contract', help='contract address', required=True)
@click.option('--task', help='the aggregator s current task id', required=True)
@click.option('--validation', required=True)
@click.option('--evaluation', required=True)
@click.option('--log', required=True)

# maybe later on u need to add the task id , for now makech 
def main(provider, abi, ipfs, account, passphrase, contract, log):
    logs = utilities.setup_logger(log, "create shard")
    
    contract = smart_contract_functions.Contract(logs, provider, abi, account, passphrase, contract)
   

    while True:
        captured_event = None  # Initialize a variable to hold the event data outside the loop
        event_filter = contract.contract.events.ShardNodes.create_filter(fromBlock='latest') 
        while True:
            new_entries = event_filter.get_new_entries()
            if new_entries:  # Check if there are new entries
                captured_event = new_entries[0]  # Save the first event (assuming you're interested in the first one)
                break  # Exit the loop after capturing the event

        if captured_event:
            shard_ip_addresses = captured_event['args']['ipAddresses']
            
            

main()
