from .utils import *

class FedAvgAggregator():
  def __init__(self, model_size, weights_loader):
    self.model_size = model_size
    self.weights_loader = weights_loader

  def aggregate(self, submissions  , scores):
    #samples = [samples for (_, _, samples, _,_) in submissions]
    # the impact a specific model update has when aggregating is measured based on its data size
    for element in scores:
      print(type(element))
    print("scores ", scores)
    normalized_scores = self.calculate_normalized_weights(scores)
    # refactor ya bent
    return weighted_fed_avg(submissions, self.model_size, normalized_scores)
  
  def calculate_normalized_weights(self,scores):
    min_score = min(scores)
    max_score = max(scores)
    normalized_weights = [(score - min_score) / (max_score - min_score) for score in scores]
    return normalized_weights
  
  def calculate_adjusted_min_max_normalized_scores(self,scores):
    min_score = min(scores)
    max_score = max(scores)
    new_max = 0.99
    new_min = 0.01
    normalized_scores = [((1 - (score - min_score) / (max_score - min_score)) * (new_max - new_min) + new_min) for score in scores]
    return normalized_scores
  

