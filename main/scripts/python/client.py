import click
import torch.nn as nn
import torch.optim as optim
import os
import time

# Get the path to the FederatedLearning directory relative to my_script.py
from FederatedLearning import trainer
from FederatedLearning import task_requester
from FederatedLearning import smart_contract_functions
from FederatedLearning import utilities
from FederatedLearning import ModelLoaders
from FederatedLearning import weights_loaders
from FederatedLearning.utilities import load_data



current_dir = os.getcwd()
print(f"Current working directory: {current_dir}")




@click.command()
@click.option('--provider', default='http://127.0.0.1:3050', help='web3 API HTTP provider to layer 2')
@click.option('--abi', default='./build/contracts/NoScore.json', help='contract abi file')
@click.option('--ipfs', default='/ip4/127.0.0.1/tcp/5001', help='IPFS api provider')
@click.option('--account', help='account address', required=True)
@click.option('--passphrase', help='zksync layer private key', required=True)
@click.option('--contract', help='contract address', required=True)
@click.option('--train', required=True)
@click.option('--test', required=True)
@click.option('--learning_rate', required=True)
@click.option('--epochs', required=True)
@click.option('--task', required=True)
def main(provider, abi, ipfs, account, passphrase, contract, train, test, learning_rate, epochs, task):
  # Get Contract
  contract_task = smart_contract_functions.Contract_zksync(provider, abi, contract, passphrase) 
  ania = contract_task.get_trainers()
  print("the registered trainers are ",ania)
  # we re doing this because when we pass args from bash script , the scripts gets them as a string for some reason  yaelmha rabi
  if not isinstance(task, int):
    try:
      task = int(task)
    except ValueError:
      # Handle invalid input gracefully (e.g., raise custom exception or use a default)
      raise ValueError("Invalid task id provided")
  if not isinstance(learning_rate, float):
    try:
      learning_rate = float(learning_rate)
    except ValueError:
      # Handle invalid input gracefully (e.g., raise custom exception or use a default)
      raise ValueError("Invalid learning rate provided")
                    
  if not isinstance(epochs, int):
    try:
      epochs = int(epochs)
    except ValueError:
      # Handle invalid input gracefully (e.g., raise custom exception or use a default)
      raise ValueError("Invalid epochs number provided")
  current_task = contract_task.get_task_byId(task)
  print("the ",current_task)
  weights_loader = weights_loaders.IpfsWeightsLoader(ipfs)
  model_loader = ModelLoaders.IpfsModelLoader(contract, weights_loader, ipfs_api=ipfs)

  # register to the system
  contract_task.register_as_trainer()
  # register to the task
  tx, tx_receipt = contract_task.register_as_trainer_task(task)
  print(tx_receipt)
  current_task = contract_task.get_task_byId(task)
  print("the ",current_task)
  print("done ")

  # wait some time before checking if the task's current phase is training

  while True:
    # get the task details to access the model cid
    time.sleep(5)
    current_task = contract_task.get_task_byId(task)
    print("the ",current_task)
    if current_task[16] == "training":
      break
    
  

  chosen_trainers = contract_task.get_trainers_task_round(task,0)
  with open('results.txt', 'a') as file:
    # to get the previous round global model weights hash
    file.write(f"chosen trainers : {chosen_trainers}\n")
  #chosen_trainers = (contract_task.zksync_provider.to_checksum_address(element) for element in chosen_trainers)

  # we can not pass to the training until the event reached required number of trainers is captured
  status = contract_task.is_element_in_array(chosen_trainers,account)
  print("status ",status)
  if status:
    # needs refactoring asap , u can t be calling functions from task pub class , u re a software engineer !!!!!!
    task_pub = task_requester.TaskRequester(ipfs)
    # iterates over the rounds number for this specific task current_task[11] is the rounds number
    # model , state_dict, model_info = task_pub.retrieve_model_from_ipfs(current_task[1],current_task[2])
    # model.load_state_dict(state_dict)
    i=0

    while True:
      # with open('results.txt', 'a') as file:
      #   # to get the previous round global model weights hash
      #   file.write(f"state now : {current_task[16]}  round {i} account {account} \n")

      if i==0:
        model = model_loader.load(current_task[1]) 
      else:
        print("god ",current_task[9])
        model = model_loader.load(current_task[1],current_task[9]) 

      # load train and test data
      train_loader = load_data(train)
      test_loader = load_data(test)
      criterion = nn.CrossEntropyLoss()
      optimizer = optim.SGD(model.parameters(), lr=learning_rate)
      model_trainer = trainer.Trainer(model,task,contract,account,ipfs)

      result = model_trainer.train(model, criterion, optimizer , train_loader, test_loader , epochs)

      # Accessing the weights of the trained model
      weights = model_trainer.get_weights(model)

      weights_path = model_trainer.store(weights)
      #here1 = model_trainer.save_weights(model)
      model_weights_ipfs_hash = model_trainer.store_weights_ipfs(weights_path)
      trainingAccuracy = utilities.float_to_int(result['train_acc'])
      validationAccuracy = utilities.float_to_int(result['val_acc'])
      update = {
        "trainingAccuracy": trainingAccuracy,
        "testingAccuracy": validationAccuracy,
        "trainingDataPoints": len(train_loader.dataset),
        "weights": model_weights_ipfs_hash,
        "timestamp": int(round(time.time() * 1000)),
        }
      print("are u with me ",chosen_trainers)
      transaction, transaction_receipt = contract_task.upload_model(update,task,chosen_trainers,i)
      with open('results.txt', 'a') as file:
        # to get the previous round global model weights hash
        file.write(f"round : {update}\n")

      # if i==0:
      #   with open('results.txt', 'a') as file:
      #     # to get the previous round global model weights hash
      #     file.write(f"round : {i}\n")
      #     file.write(f"Global model : {current_task[1]}\n")
      #     file.write(f"Global weights: {current_task[9]}\n")
      # else:
      #     with open('results.txt', 'a') as file:
      #       # to get the previous round global model weights hash
      #       file.write(f"round : {i}\n")
      #       file.write(f"Global model : {current_task[1]}\n")
      #       file.write(f"Global weights: {captured_event['args']['globalModelWeightsCID']}\n")
  
      i+=1
      while True and i!=current_task[11] :
        time.sleep(10)
        # get the task details to access the model cid
        current_task = contract_task.get_task_byId(task)
        if current_task[16] == "training":
          break

      



      if i==current_task[11]:
        break
      time.sleep(0.5)
  else:
    print("trainer is not selected for the task ")

main()  