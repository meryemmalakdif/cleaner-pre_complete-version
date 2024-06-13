from .utils import *

class FedAvgAggregator():
  def __init__(self, model_size, weights_loader):
    self.model_size = model_size
    self.weights_loader = weights_loader

  def aggregate(self, trainers, submissions , trainer , scores):
    #samples = [samples for (_, _, samples, _,_) in submissions]
    # the impact a specific model update has when aggregating is measured based on its data size
    normalized_scores = self.calculate_normalized_weights(scores)
    # refactor ya bent
    return weighted_fed_avg(submissions, self.model_size, trainer, normalized_scores)
  
  def calculate_normalized_weights(self,scores):
    min_score = min(scores)
    max_score = max(scores)
    print("aggregation algorithm ",scores)
    normalized_weights = [(score - min_score) / (max_score - min_score) for score in scores]
    return normalized_weights

