import numpy as np
from ..utilities import floats_to_ints

class GroupInstanceDeletion():
  def __init__(self, weights_loader, aggregator_type) -> None:
    # aggregator_type : fedavg , fedprox ...
    self.weights_loader = weights_loader
    self.aggregator_type = aggregator_type

  def evaluate_one_submission(self, model , test_dataloader, criterion, submissions,submission_indice, trainer, aggregator, scores):
    # Exclude client's submission from the submissions 
    submissions_excluded = [submission for idx, submission in enumerate(submissions) if idx != submission_indice]
    scores_excluded = [score for idx, score in enumerate(scores) if idx != submission_indice]

    # aggregate while considering the client weights 
    global_model_weights = self.aggregator_type.aggregate([], submissions , trainer, scores)
    model.set_weights(model,global_model_weights)
    # calculate accuracy of the global model including the client weights
    results = aggregator.validate(model , test_dataloader, criterion)
    # aggregating while excluding the client weights
    global_model_weights_excluded = self.aggregator_type.aggregate([],submissions_excluded,trainer, scores_excluded)
    model.set_weights(model,global_model_weights_excluded)
    # calculate accuracy of the global model excluding the client weights
    results_excluded = aggregator.validate(model , test_dataloader, criterion)

    # calculate the difference in accuracy and loss
    accuracy_gain = results['accuracy'] - results_excluded['accuracy']
    loss_difference = results['average_loss'] - results_excluded['average_loss']
    return {'accuracy_gain': accuracy_gain, 'loss_difference': loss_difference}


  def evaluate(self, trainers, model , test_dataloader, criterion, submissions, trainer, aggregator):
    accuracy_results = []
    loss_results = []
    for i in range(len(submissions)):
      evaluate_single_submission = self.evaluate_one_submission(model , test_dataloader, criterion, submissions, i , trainer, aggregator)
      accuracy_results.append(evaluate_single_submission['accuracy_gain'])
      loss_results.append(evaluate_single_submission['loss_difference'])
    # later when u store these on the blockchain u need to make them int 
    # accuracy_results = floats_to_ints(accuracy_results)
    # loss_results = floats_to_ints(loss_results)
    return trainers, accuracy_results, loss_results
