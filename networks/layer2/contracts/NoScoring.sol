// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

import './MainContract.sol';

contract NoScore is MainContract {
  // constructor(string memory _model, string memory _weights) MainContract(
  //   _model,
  //   _weights,
  //   RoundPhase.WaitingForAggregations
  // ) { }

    constructor() MainContract(
  
    ) { }

  // function startRound(address[] memory roundTrainers, address[] memory roundAggregators) public {
  //   require(msg.sender == owner, "Only the owner can start a round");
  //   require(roundPhase == RoundPhase.Stopped, "NS");
  //   require(roundTrainers.length > 0, "No trainers found");
  //   require(roundAggregators.length > 0, "Not a single aggregation found");
  //   require(aggregators.length > 0 && trainers.length > 0, "NO trainers nor aggregators found");

  //   round++;
  //   selectedTrainers[round] = roundTrainers;
  //   selectedAggregators[round] = roundAggregators;
  //   roundPhase = RoundPhase.WaitingForUpdates;
  // }
}
