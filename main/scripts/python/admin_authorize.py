import click
import os
import time

# Get the path to the FederatedLearning directory relative to my_script.py
from FederatedLearning import smart_contract_functions




current_dir = os.getcwd()
print(f"Current working directory: {current_dir}")




@click.command()
@click.option('--provider_layer1', default='http://127.0.0.1:8545', help='web3 API HTTP provider for layer 1')
@click.option('--abi_oracle', default='', help='oracle contract abi file')
@click.option('--account', help='account address needed to interact with the layer 2 and layer 1', required=True)
@click.option('--passphrase', help='private key needed to interact with the layer 2 and layer 1', required=True)
@click.option('--contract_oracle', help='oracle contract address', required=True)
@click.option('--oracle_node', help='oracle node address', required=True)
def main(provider_layer1, abi_oracle, account, passphrase, contract_oracle, oracle_node):
  # we re doing this because when we pass args from bash script , the scripts gets them as a string for some reason  yaelmha rabi
  if not isinstance(passphrase, str):
    try:
      passphrase = str(passphrase)
    except ValueError:
      # Handle invalid input gracefully (e.g., raise custom exception or use a default)
      raise ValueError("Invalid private key provided")  
 
  # Get the oracle contract
  contract_layer1 = smart_contract_functions.Contract(provider_layer1, abi_oracle, contract_oracle, passphrase)
  # use the account of metamask as admin aka the one that deployed the operator contract
  senders = [oracle_node]
  
  tx, tx_receipt = contract_layer1.authorize(senders)
  







      



main()  