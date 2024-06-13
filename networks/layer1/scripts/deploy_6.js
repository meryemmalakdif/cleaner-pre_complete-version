async function main() {
    const [deployer] = await ethers.getSigners();
    console.log("Deploying contracts with the account:", deployer.address);
  
    const MyContract = await ethers.getContractFactory("Math");
    const myContract = await MyContract.deploy();
    const addressi=  await myContract.getAddress();
    console.log("Deployed address:" + myContract.address);
    console.log("MyContract deployed to:", addressi);
  }


  
  main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
    });
  