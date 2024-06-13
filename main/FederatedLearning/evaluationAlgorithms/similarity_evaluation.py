import numpy as np
from ..utilities import floats_to_ints

class SimilarityBasedEvaluation():
  def __init__(self, weights_loader) -> None:
    self.weights_loader = weights_loader

  def evaluate(self, trainers, submissions):

    R = len(submissions)
    # the maximum number of faulty or malicious updates the algorithm can tolerate
    f = R // 3 - 1
    # number of closest updates considered
    closest_updates = R - f - 2

    weights_cids = [cid for (_, _, _, cid,_) in submissions]
    # here we are extracting the weights from the ipfs
    weights = [self.weights_loader.load(cid) for cid in weights_cids]

    similarities = []

    for i in range(len(weights)):
      dists = []

      for j in range(len(weights)):
        if i == j:
          # pass because its the same weight
          continue
        dists.append(np.linalg.norm(weights[j] - weights[i]))

      # take the first elements which refer to the smallest distances
      dists_sorted = np.argsort(dists)[:closest_updates]
      similarity = np.array([dists[i] for i in dists_sorted]).sum()
      similarities.append(similarity)

    # later on when u store it on the blockchain
    #similarities = floats_to_ints(similarities)
    return trainers, similarities , []
