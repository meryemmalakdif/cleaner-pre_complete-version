async function main() {
    const [deployer] = await ethers.getSigners();
    console.log("Deploying contracts with the account:", deployer.address);
  
    const MyContract = await ethers.getContractFactory("LinkToken");
    //const myContract = await MyContract.deploy("QmYjSQ9xCkRu8NH8aXi9RLgWE1wekVwthWrk6hoeWFBH2X", "");
    const myContract = await MyContract.deploy();
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
  
    