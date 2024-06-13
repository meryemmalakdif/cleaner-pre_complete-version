async function main() {
    const [deployer] = await ethers.getSigners();
    console.log("Deploying contracts with the account:", deployer.address);
  
    const MyContract = await ethers.getContractFactory("NoScore");
    //const myContract = await MyContract.deploy("QmYjSQ9xCkRu8NH8aXi9RLgWE1wekVwthWrk6hoeWFBH2X", "");
    const myContract = await MyContract.deploy("0x6a823A9BE9800B588c74B96A4D310EF54f729164");
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
  
    