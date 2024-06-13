import torch

# scores trainers based on their marginal gain (improvement in accuracy) compared to the previous round
class MarginalGainBasedEvaluation():
  def __init__(self, weights_loader) -> None:
    self.weights_loader = weights_loader
    self.c = {}

  def evaluate(self, trainers, submissions, model , test_dataloader, criterion):
    # Gets the accuracy from the previous round's global model
    last_accuracy = self.calculate_accuracy(model , test_dataloader, criterion)
    print("submissions ",submissions)
    for i, submission in enumerate(submissions):
      trainer = trainers[i]
      # self.c a storage for each trainer's cumulative marginal gain
      # cumulative marginal gain is used to encourage stable and long-term improvement and not only occasional good performance
      if trainer not in self.c:
        # its the trainer's first time
        self.c[trainer] = 0

      (_, _, _, weights_cid) = submission
      print("weights cid from marginal gain ",weights_cid)
      if weights_cid!='':
        weights = self.weights_loader.load(weights_cid)
        model.set_weights(model,weights)
        local_model_accuracy = self.calculate_accuracy(model , test_dataloader, criterion)
        self.c[trainer] += local_model_accuracy - last_accuracy

    # gives the score based on the marginal accuracy
    #scores = [0 if self.c[trainer] < 0 else self.c[trainer] for trainer in trainers]
    scores = [self.c[trainer] for trainer in trainers]
    return trainers, scores , []


  def calculate_accuracy(self, model , test_dataloader, criterion):
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
    return accuracy
