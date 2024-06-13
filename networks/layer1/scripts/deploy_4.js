async function main() {
    const [deployer] = await ethers.getSigners();
    console.log("Deploying contracts with the account:", deployer.address);
  
    const MyContract = await ethers.getContractFactory("APIConsumer");
    //const myContract = await MyContract.deploy("QmYjSQ9xCkRu8NH8aXi9RLgWE1wekVwthWrk6hoeWFBH2X", "");
    const myContract = await MyContract.deploy("0xbe8582a2aAD675b6909732d1cB69dc5Ac15744dD","0xb0F5C5dCcd4Acec2d73f90E5003eEE620835573F");
    const addressi=  await myContract.getAddress();
    console.log("Deployed address:" + myContract.address);
    console.log("no score contract deployed to:", addressi);
  }


  
  main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
    });
  