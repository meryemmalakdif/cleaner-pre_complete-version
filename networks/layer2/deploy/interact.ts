import * as hre from "hardhat";
import { getWallet } from "./utils";
import { ethers } from "ethers";


// An example of a script to interact with the contract
export default async function (contractAddress , artifact ) {
  console.log(`Running script to interact with contract ${contractAddress}`);

  // Load compiled contract info
  const contractArtifact = await hre.artifacts.readArtifact(artifact);

  // Initialize contract instance for interaction
  const contract = new ethers.Contract(
    contractAddress,
    contractArtifact.abi,
    getWallet() // Interact with the contract on behalf of this wallet
  );

  return contract;

  // // Run contract and interact with its functions
  // const response = await contract.greet();
  // console.log(`Current message is: ${response}`);

  // // Run contract write function
  // const transaction = await contract.setGreeting("Hello people!");
  // console.log(`Transaction hash of setting new message: ${transaction.hash}`);

  // // Wait until transaction is processed
  // await transaction.wait();

  // // Read message after transaction
  // console.log(`The message now is: ${await contract.greet()}`);
}
