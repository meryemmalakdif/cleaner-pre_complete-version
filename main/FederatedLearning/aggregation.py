import json
import time
import torch

class Aggregator():
  def __init__(self, task, contract, weights_loader, model_loader, aggregator, model, address):
    self.currentTask = task
    self.weights_loader = weights_loader
    self.model_loader = model_loader
    self.contract = contract
    #(self.x_train, self.y_train, self.x_test, self.y_test) = data
    self.aggregator = aggregator
    self.model = model
    self.address = address
    # register to the system
    self.__register_aggregator()
    # register to the task
    self.__register_aggregator_task(self.currentTask)

  def aggregate(self, trainer, round, submissions, scores):
    with open('results.txt', 'a') as file:
      # to get the previous round global model weights hash
      file.write(f"trainers : {self.currentTask[7]}\n")

    new_weights = self.aggregator.aggregate([], submissions , trainer, scores)
    weights_cid = self.weights_loader.store(new_weights)
    tx , tx_receipt = self.contract.submit_aggregation(weights_cid,self.currentTask[0],self.currentTask[8],round)
    return weights_cid, tx, tx_receipt
  
  def get_global_model_weights(self):
    model_cid = self.currentTask[1]
    weights_cid = self.currentTask[9]
    return self.model_loader.load(model_cid,weights_cid)

  def validate(self,model , test_dataloader, criterion):
    model.eval()  # Set the model to evaluation mode
    total_loss = 0.0
    correct_predictions = 0
    total_samples = 0

    with torch.no_grad():  # Disable gradient computation
      for inputs, labels in test_dataloader:
        #inputs, labels = inputs.to(device), labels.to(device)  # Move data to the same device as the model
        outputs = model(inputs)  # Get model predictions
        loss = criterion(outputs, labels)  # Calculate loss
        total_loss += loss.item()  # Aggregate loss
        _, predicted = torch.max(outputs, 1)  # Get the predicted class
        correct_predictions += (predicted == labels).sum().item()  # Count correct predictions
        total_samples += labels.size(0)  # Count total samples

    # Calculate average loss and accuracy
    average_loss = total_loss / len(test_dataloader)
    accuracy = correct_predictions / total_samples
    return {'average_loss': average_loss, 'accuracy': accuracy}


  def __register_aggregator(self):
    self.contract.register_as_aggregator()

  def __register_aggregator_task(self,task):
    task_aggregators = self.contract.get_aggregators_task(task[0])
    if self.contract.is_element_in_array(task_aggregators,self.address) == False:
      tx,tx_receipt = self.contract.register_as_aggregator_task(task[0])
      self.currentTask=self.contract.get_task_byId(self.currentTask[0])


  # contributions file has trainers array and contributions array 
  def store_contributions_locally(self, trainers, contributions, contributions_path='contributions.json'):
    data = {
        "trainers": trainers,
        "contributions": contributions
    }
    with open(contributions_path, 'w') as file:
        json.dump(data, file, indent=2)
    return contributions_path
  
  # read contributions from a file
  def read_contributions_locally(self, contributions_path='contributions.json'):
    with open(contributions_path, 'r') as file:
        data = json.load(file)
    
    return data['trainers'], data['contributions']