import click
import os
import time

# Get the path to the FederatedLearning directory relative to my_script.py
from FederatedLearning import smart_contract_functions




current_dir = os.getcwd()
print(f"Current working directory: {current_dir}")




@click.command()
@click.option('--provider', default='http://127.0.0.1:3050', help='web3 API HTTP provider for layer 2')
@click.option('--provider_layer1', default='http://127.0.0.1:8545', help='web3 API HTTP provider for layer 1')
@click.option('--abi', default='', help='contract abi file')
@click.option('--abi_oracle', default='', help='oracle contract abi file')
@click.option('--abi_rep', default='', help='reputation contract abi file')
@click.option('--ipfs', default='/ip4/127.0.0.1/tcp/5001', help='IPFS api provider')
@click.option('--account', help='account address needed to interact with the layer 2 and layer 1', required=True)
@click.option('--passphrase', help='private key needed to interact with the layer 2 and layer 1', required=True)
@click.option('--contract', help='task contract address', required=True)
@click.option('--contract_oracle', help='oracle contract address', required=True)
@click.option('--contract_rep', help='reputation contract address', required=True)
@click.option('--task', required=True) 
@click.option('--evaluation', required=True) 
def main(provider, provider_layer1,  abi, abi_oracle, abi_rep, ipfs, account, passphrase, contract, contract_oracle, contract_rep, task, evaluation):
  # we re doing this because when we pass args from bash script , the scripts gets them as a string for some reason  yaelmha rabi
  if not isinstance(passphrase, str):
    try:
      passphrase = str(passphrase)
    except ValueError:
      # Handle invalid input gracefully (e.g., raise custom exception or use a default)
      raise ValueError("Invalid private key provided")  
  if not isinstance(evaluation, str):
    try:
      evaluation = str(evaluation)
    except ValueError:
      # Handle invalid input gracefully (e.g., raise custom exception or use a default)
      raise ValueError("Invalid evaluation method")  
  if not isinstance(task, int):
    try:
      task = int(task)
    except ValueError:
      # Handle invalid input gracefully (e.g., raise custom exception or use a default)
      raise ValueError("Invalid task id provided")
    
  # Get the oracle contract
  contract_layer1 = smart_contract_functions.Contract(provider_layer1, abi_oracle, contract_oracle, passphrase)

  contract_task = smart_contract_functions.Contract_zksync(provider, abi, contract, passphrase)

  # Get access to reputation contract -deployed on layer 2- functions
  contract_reputation = smart_contract_functions.Contract_zksync(provider, abi_rep, contract_rep, passphrase)
  
  while True:
    time.sleep(10)
    # get the task details to access the model cid
    current_task = contract_task.get_task_byId(task)
    if current_task[16] == "evaluation":
      print("holaaa ")
      break  
  i=0

  while True:

    initial_trainers , local_updates = contract_task.get_updates_task(task,current_task[10])
    
    local_weights_elements = [item[3] for item in local_updates]
    local_models_time = [item[4] for item in local_updates]
    local_hash = "-".join(local_weights_elements)
    trainers = "-".join(initial_trainers)
    print("works  ",local_hash, "  ", trainers, "  ", current_task[1] , "  ", current_task[9] , "  ", evaluation)
    if current_task[9]:
      global_model_weights = current_task[9]
    else:
      global_model_weights=""
    tx, tx_receipt = contract_layer1.evaluation_admin(local_hash, trainers, current_task[1] , global_model_weights , evaluation)
    print("meryeem ",tx_receipt)
    sc = contract_layer1.scores_admin()     
    
    while len(sc) == 0:
      sc = contract_layer1.scores_admin() 

    ##sc = [abs(element) for element in sc]

    with open('michou.txt', 'a') as file:
        file.write(f"the result to be stored in BC is : {sc}\n")
      

    result = list(zip(initial_trainers, sc, local_models_time))
    
    contract_task.upload_scores(task,current_task[10],result)
    scores_round = contract_task.get_scores_task_round(task,i)
    # with open('michou.txt', 'a') as file:
    #     file.write(f"rounds scores : {scores_round}\n")
    sc = [str(element) for element in sc]
    models_scores = "-".join(sc)

    tx, tx_receipt = contract_layer1.trigger_aggregation_admin(local_hash, models_scores, current_task[1])
    global_model_weights_hash = contract_layer1.get_global_model_weights_hash()
    while global_model_weights_hash == "":
      global_model_weights_hash = contract_layer1.get_global_model_weights_hash()
    
    if (i+1)%2 == 0:
      task_state = "reputation"
    else:
      task_state = "training"
    
     
    contract_task.update_global_model_weights(task,global_model_weights_hash,task_state)
    while True: 
      gg = contract_task.get_task_byId(task)
      if(gg[9] == global_model_weights_hash):
        break

    # with open('michou.txt', 'a') as file:
    #     file.write(f"global model received : {global_model_weights_hash}\n")
    #     file.write(f"global model stored : {gg[9]}\n")
    #     file.write(f"current round : {i}\n")
    

    if (i+1)%2 == 0:    
      if (i+1) != current_task[11]:  
        for worker in initial_trainers:
          level = contract_task.get_total_participation_level(worker)

          contract_reputation.update_reputation(task, i-1 , i+1, worker , evaluation )
          # interactions = contract_reputation.filter_event1("interactionsTP", "interactionsTP(uint256,uint256)")

          # ff = contract_reputation.filter_event1("scoresFetched", "scoresFetched(int256[])")
          # ff1 = contract_reputation.filter_event1("recencyGot", "recencyGot(uint256)")
          # ff2 = contract_reputation.filter_event1("performanceMeasured", "performanceMeasured(uint256,uint256)")
          # ff3 = contract_reputation.filter_event1("scoreTrainerFetched", "scoreTrainerFetched(int256)")

          
          with open('performance.txt', 'a') as file:
            file.write(f"{worker}  level of participation : {level} \n")
          #   # file.write(f"scores fetched : {ff} \n")
          #   # file.write(f"recency got : {ff1} \n")
          #   # file.write(f"performance measured : {ff2} \n")
          #   file.write(f"trainer score : {ff3} \n")
          all_reputation = contract_task.get_all_reputation()
          with open('michou.txt', 'a') as file:
            file.write(f"reputation : {all_reputation}\n") 
          

        contract_task.update_task_state(task,"selection")
        while True:
          # get the task details to access the model cid
          current_task = contract_task.get_task_byId(task)
          if current_task[16] == "selection":
            break

      else:
        contract_task.update_task_state(task,"done")


    else:

      contract_task.update_task_state(task,"training")
      while True:
        # get the task details to access the model cid
        current_task = contract_task.get_task_byId(task)
        if current_task[16] == "training":
          break

    with open('submissions.txt', 'a') as file:
      file.write(f"miloo : {current_task[16]}\n")
    i+=1    
 
    while True:
      time.sleep(10)
      # get the task details to access the model cid
      current_task = contract_task.get_task_byId(task)
      if current_task[16] == "evaluation" or i == current_task[11]:
        break
    # measure reputation at time slots
    # we got scores using method of similarity weights for example
    current_time = int(round(time.time() * 1000))
    


    if i == current_task[11]:
      break
    time.sleep(0.5)
    # scores = [utilities.int_to_float(value) for value in captured_event['args']['volume']]
    # print(scores)
    # # now we need to store the scores in the blockchain for the current round
    # result = list(zip(initial_trainers, captured_event['args']['volume'], local_models_time))
    # with open('mimi.txt', 'a') as file:
    #   file.write(f"the result to be stored in BC is : {result}\n")
    # contract.upload_scores(task,current_task[10],result)


    

# use the account of metamask as admin aka the one that deployed the operator contract
# senders = ["0x46DfE44B89e8c0F53b577eace5a8A3D68656C3D9"]
# tx, tx_receipt = scontract.authorize(["0x46DfE44B89e8c0F53b577eace5a8A3D68656C3D9"])




      



main()  