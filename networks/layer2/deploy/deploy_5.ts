import { deployContract } from "./utils";

// An example of a basic deploy script
// It will deploy a Greeter contract to selected network
// as well as verify it on Block Explorer if possible for the network
export default async function () {
  const contractArtifactName = "ManageReputation";
  const constructorArguments = ["0xDe9BFE17987aF53F4b9A1d09a2431f544ECd9EA9"];
  await deployContract(contractArtifactName,constructorArguments);
}

// yarn hardhat deploy-zksync --script deploy-my-contract.ts
