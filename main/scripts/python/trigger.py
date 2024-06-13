# Hack path so we can load 'blocklearning'
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
import logging
import time
import random
import json
from FederatedLearning import smart_contract_functions
from FederatedLearning import utilities




@click.command()
@click.option('--provider', default='http://127.0.0.1:8545', help='web3 API HTTP provider')
@click.option('--abi', default='./build/contracts/NoScore.json', help='contract abi file')
@click.option('--account', help='ethereum account to use for this computing server', required=True)
@click.option('--passphrase', help='passphrase to unlock account', required=True)
@click.option('--contract', required=True, help='contract address')
@click.option('--rounds', default=1, type=click.INT, help='number of rounds')
@click.option('--log', required=True)
def main(provider, abi, account, passphrase, contract, rounds, log):
  logs = utilities.setup_logger(log, "trigger")
  contract = smart_contract_functions.Contract(logs, provider, abi, account, passphrase, contract)

#   x_val, y_val = butilities.numpy_load(val)
  all_trainers = contract.get_trainers()
  all_aggregators = contract.get_aggregators()
  round_trainers = all_trainers
  round_aggregators = all_aggregators


#   def eval_model(weights):
#     log.info(json.dumps({ 'event': 'eval_start', 'ts': time.time_ns(), 'round': round }))
#     model.set_weights(weights_loader.load(weights))
#     metrics = model.evaluate(x_val, y_val)
#     accuracy = metrics['sparse_categorical_accuracy']
#     log.info(json.dumps({ 'event': 'eval_end', 'ts': time.time_ns(), 'round': round }))
#     return accuracy

  for i in range(0, rounds):
    logs.info(json.dumps({ 'event': 'start', 'trainers': round_trainers, 'aggregators': round_aggregators, 'ts': time.time_ns() }))

    contract.start_round(round_trainers, round_aggregators)
    round = contract.get_round()
    print("current round ", round)

    # while contract.get_round_phase() != blocklearning.RoundPhase.WAITING_FOR_TERMINATION:
    #   time.sleep(0.25)

    # contract.terminate_round()
    # weights = contract.get_weights(round)
    # accuracy = eval_model(weights)

    # log.info(json.dumps({ 'event': 'end', 'ts': time.time_ns(), 'round': round, 'weights': weights, 'accuracy': butilities.float_to_int(accuracy) }))

main()
