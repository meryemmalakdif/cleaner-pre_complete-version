import json
import time
from ..utilities import numpy_load, float_to_int

class Evaluator():
  def __init__(self, log, contract, model, weights_loader, val) -> None:
    self.log = log
    self.contract = contract
    self.model = model
    # loads weights from ipfs giving a CID
    self.weights_loader = weights_loader
    x_val, y_val = numpy_load(val)
    self.val = (x_val, y_val)

  def eval_round(self, round):
    # evaluation will not be performed
    if round == 0:
      return float_to_int(0)
    # returns the content ID of the weights from the blockchain using smart contract
    weights_cid = self.contract.get_weights(round)
    # extracts the real weights from the ipfs
    weights = self.weights_loader.load(weights_cid)
    return self.eval(round, weights)

  def eval(self, round, weights):
    self.model.set_weights(weights)
    self.log.info(json.dumps({ 'event': 'eval_start', 'round': round,'ts': time.time_ns() }))
    metrics = self.model.evaluate(self.val[0], self.val[1])
    accuracy = float_to_int(metrics['sparse_categorical_accuracy'])
    self.log.info(json.dumps({ 'event': 'eval_end', 'round': round,'ts': time.time_ns() }))
    return accuracy
