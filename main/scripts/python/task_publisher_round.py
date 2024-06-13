
import click
import torch
import torch.nn as nn
import torch.optim as optim
import os
import time

# Get the path to the FederatedLearning directory relative to my_script.py
from FederatedLearning import task_requester
from FederatedLearning import smart_contract_functions
from FederatedLearning import ModelLoaders
from FederatedLearning import utilities



current_dir = os.getcwd()
print(f"Current working directory: {current_dir}")




@click.command()
@click.option('--provider', default='http://127.0.0.1:3050', help='web3 API HTTP provider for layer 2')
@click.option('--abi', default='./build/contracts/NoScore.json', help='contract abi file')
@click.option('--ipfs', default='/ip4/127.0.0.1/tcp/5001', help='IPFS api provider')
@click.option('--account', help='account address')
@click.option('--passphrase', help='account private key')
@click.option('--contract', help='contract address', required=True)
@click.option('--task', required=True)
def main(provider, abi, ipfs, account, passphrase, contract, task):
  contract_task = smart_contract_functions.Contract_zksync(provider, abi, contract, passphrase) 
  current_round = 0
  time.sleep(10)
  if not isinstance(task, int):
    try:
      task = int(task)
    except ValueError:
      # Handle invalid input gracefully (e.g., raise custom exception or use a default)
      raise ValueError("Invalid task id provided")
  the_task = contract_task.get_task_byId(task)
  task_requester_instance = task_requester.TaskRequester(ipfs)
  selected_trainers = task_requester_instance.selectTrainers(the_task[14],the_task[12])

  current_task = contract_task.get_task_byId(task)
  while True:
    contract_task.set_task_trainers_round(task,current_round,selected_trainers)
    current_round+=2 ## u increment it by the frequency of the clients selection
    if current_round == current_task[11]:
      break

    while True:
      time.sleep(10)
      # get the task details to access the model cid
      current_task = contract_task.get_task_byId(task)
      with open('updates.txt', 'a') as file:
        file.write(f"state  : {current_task[16]}\n")
      if current_task[16] == "selection":
        break


main()
