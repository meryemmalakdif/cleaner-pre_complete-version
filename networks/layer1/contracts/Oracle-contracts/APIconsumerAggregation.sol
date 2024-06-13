// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import "@chainlink/contracts/src/v0.8/shared/access/ConfirmedOwner.sol";

/**
 * Request testnet LINK and ETH here: https://faucets.chain.link/
 * Find information on LINK Token Contracts and get the latest ETH and LINK faucets here: https://docs.chain.link/docs/link-token-contracts/
 */

/**
 * THIS IS AN EXAMPLE CONTRACT WHICH USES HARDCODED VALUES FOR CLARITY.
 * THIS EXAMPLE USES UN-AUDITED CODE.
 * DO NOT USE THIS CODE IN PRODUCTION.
 */


contract APIConsumerAggregation is ChainlinkClient, ConfirmedOwner {
    using Chainlink for Chainlink.Request;

    string public globalModelWeightsHash;
    bytes32 private jobId;
    uint256 private fee;

    event RequestVolume(bytes32 indexed requestId, string volume);

    /**
     * @notice Initialize the link token and target oracle
     *
     * Sepolia Testnet details:
     * Link Token: 0x779877A7B0D9E8603169DdbD7836e478b4624789
     * Oracle: 0x6090149792dAAeE9D1D568c9f9a6F6B46AA29eFD (Chainlink DevRel)
     * jobId: ca98366cc7314957b8c012c72f05aeeb
     *
     */
    constructor(address _linkContract, address _oracleContract) ConfirmedOwner(msg.sender) {
        _setChainlinkToken(_linkContract);
        _setChainlinkOracle(_oracleContract);
        jobId = "29d52bd7a2ba469e9bd8b34d0a291d24";
        fee = (1 * LINK_DIVISIBILITY) / 10; // 0,1 * 10**18 (Varies by network and job)
    }


    // call when aggregating
    function requestAggregation(string memory local_models, string memory scores, string memory model_hash) public returns (bytes32 requestId) {
    Chainlink.Request memory req = _buildChainlinkRequest(
        jobId,
        address(this),
        this.fulfillAggregation.selector
    );
    
    // Set the URL to perform the GET request on
    req._add("local_models",local_models);
    req._add("scores",scores);
    req._add("global_model_hash",model_hash);

    // Sends the request
    return _sendChainlinkRequest(req, fee);
    }


    /**
     * Receive the response in the form of string
     */
    function fulfillAggregation(
        bytes32 _requestId,
        string memory _volume
    ) public recordChainlinkFulfillment(_requestId) {
        emit RequestVolume(_requestId, _volume);
        globalModelWeightsHash = _volume;
    }

    /**
     * Allow withdraw of Link tokens from the contract
     */
    function withdrawLink() public onlyOwner {
        LinkTokenInterface link = LinkTokenInterface(_chainlinkTokenAddress());
        require(
            link.transfer(msg.sender, link.balanceOf(address(this))),
            "Unable to transfer"
        );
    }

    function getVolume() public view returns (string memory) {
    return globalModelWeightsHash;
}
}