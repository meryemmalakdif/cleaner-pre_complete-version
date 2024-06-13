import web3
import time
import click
import torch.nn as nn
# Get the path to the FederatedLearning directory relative to my_script.py
from FederatedLearning import trainer
from FederatedLearning import task_requester
from FederatedLearning import smart_contract_functions
from FederatedLearning import utilities
from FederatedLearning.utilities import load_data
from FederatedLearning import aggregation_algorithms
from FederatedLearning import *
from FederatedLearning import ModelLoaders
from FederatedLearning import weights_loaders
from FederatedLearning import evaluationAlgorithms

@click.command()
@click.option('--provider', default='http://127.0.0.1:3050', help='web3 API HTTP provider for layer 2')
@click.option('--provider_layer1', default='http://127.0.0.1:8545', help='web3 API HTTP provider for layer 1')
@click.option('--abi', default='', help='contract abi file')
@click.option('--abi_oracle', default='', help='oracle contract abi file')
@click.option('--ipfs', default='/ip4/127.0.0.1/tcp/5001', help='IPFS api provider')
@click.option('--account', help='account address needed to interact with the layer 2 and layer 1', required=True)
@click.option('--passphrase', help='private key needed to interact with the layer 2 and layer 1', required=True)
@click.option('--contract', help='task contract address', required=True)
@click.option('--contract_oracle', help='oracle contract address', required=True)
@click.option('--task', required=True) 
@click.option('--validation', required=True)
def main(provider, provider_layer1,  abi, abi_oracle, ipfs, account, passphrase, contract, contract_oracle, task, validation):
    if not isinstance(task, int):
        try:
            task = int(task)
        except ValueError:
            # Handle invalid input gracefully (e.g., raise custom exception or use a default)
            raise ValueError("Invalid task id provided")
    contract_task = smart_contract_functions.Contract_zksync(provider, abi, contract, passphrase)
    contract_layer1 = smart_contract_functions.Contract(provider_layer1, abi_oracle, contract_oracle, passphrase)

    # register to the system
    contract_task.register_as_aggregator()
    # register to the task
    tx, tx_receipt = contract_task.register_as_aggregator_task(task)
    weights_loader = weights_loaders.IpfsWeightsLoader(ipfs)
    model_loader = ModelLoaders.IpfsModelLoader(contract_task, weights_loader, ipfs_api=ipfs)
    # here the starting round should be the task's current round and not always 0
    while True:
        time.sleep(10)
        # get the task details to access the model cid
        current_task = contract_task.get_task_byId(task)
        if current_task[16] == "aggregation":
            break
    



    status = contract_task.is_element_in_array(current_task[8],account)
    print("status ",status)
    if status:

        i=0



        while True:



            task_pub = task_requester.TaskRequester(ipfs)
            model = model_loader.load(current_task[1]) 
            # aggregation method
            fed_avg_aggregator = aggregation_algorithms.FedAvgAggregator(ModelLoaders.Model(model).count, weights_loader)
            
            
            # I need to pass the captured models to the aggregator 
            # refactoring needed ASAP

            model_trainer = trainer.Trainer(model,task,contract_task,account,ipfs)



            _aggregator = Aggregator(current_task, contract_task, weights_loader, model_loader, fed_avg_aggregator, model, account)
            
            
            # self.currentTask[0],self.currentTask[7] => task id and task participating trainers respectively
            task_trainers ,  submissions = contract_task.get_updates_task(current_task[0],i)

            validation_loader = load_data(validation)
            criterion = nn.CrossEntropyLoss()

            # trainers, accuracy_results, loss_results = _aggregator.evaluate(model , validation_loader, criterion , model_trainer, submissions)
            # here we store the contribution measeurement and the trainers list on the ipfs 
            # _aggregator.store_contributions_locally(trainers,accuracy_results)
            
            # t , c = _aggregator.read_contributions_locally()
            # print("reading data from local ")
            # print(t)
            # print(c)
            # # here we store the returned ipfs cid on the blockchain 

            # print("Evaluation mode now ")
            # print(trainers)
            # print(accuracy_results)
            # print(loss_results)
            # with open(evaluation+'.txt', 'a') as file:
            #     # Write the loss and accuracy to the file
            #     file.write(f"round : {i}\n")
            #     file.write(f"accuracy difference : {accuracy_results}\n")
            #     file.write(f"loss difference : {loss_results}\n")

            only_scores = contract_task.get_scores_task_round(task,i) 
            # with open('trainers.txt', 'a') as file:
            #     file.write(f"the scores are : {only_scores}\n") 
            weights_cid , transaction, transaction_receipt = _aggregator.aggregate(model_trainer,i,submissions,only_scores)


            # global_model_weights = weights_loader.load(weights_cid)
            # print("global_model_weights ", global_model_weights)
            # model.set_weights(model,global_model_weights)
            # validation_loader = load_data(validation)
            # criterion = nn.CrossEntropyLoss()

            # no need for this
            result = _aggregator.validate(model,validation_loader,criterion)
            # print("global model loss ",result['average_loss'])
            # print("global model accuracy ",result['accuracy'])
            # print("aggregator done !!") 
            # print("number of rounds ",current_task[11] , "current round from aggregator ",i)


            contract.update_global_model_weights(task,weights_cid)
            # next round
            i+=1
            while True:
                time.sleep(10)
                # get the task details to access the model cid
                current_task = contract_task.get_task_byId(task)
                if current_task[16] == "aggregation":
                    break
            # check if it reached the task's total rounds number
            if i==current_task[11]:
                break
            time.sleep(0.5)




            # u need to get the accuracy of the global model based on a specific dataset
            # leave a portion for that when u split data between clients
            #print(global_model)
            # now aggregations are submitted
            # lets fetch the aggregated model and test it 
    
            
    # This is usefull when all the task aggregators have submitted their respective global models 
    # Once it is done , we can go to the next round
    # for now am working like I only have one aggregator , 
    # later on when I have multiple ones I need to set the task global model as the one submitted 
    # by a maximum number of aggregators 

    # captured_event_all_aggregations = None  # Initialize a variable to hold the event data outside the loop
    # event_filter_all_aggregations = contract.contract.events.AllAggregationsSubmitted.create_filter(fromBlock='latest') 
    
    # while True:
    #     #print("aggregator is in that loop")
    #     new_entries_all_aggregations = event_filter_all_aggregations.get_new_entries()
    #     if new_entries_all_aggregations:  # Check if there are new entries
    #         captured_event_all_aggregations = new_entries_all_aggregations[0]  # Save the first event (assuming you're interested in the first one)
    #         print("Aggregations submitted to bc event", captured_event_all_aggregations)
    #         break  # Exit the loop after capturing the event

main()
