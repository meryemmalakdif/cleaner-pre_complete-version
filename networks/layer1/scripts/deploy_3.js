async function main() {
    const [deployer] = await ethers.getSigners();
    console.log("Deploying contracts with the account:", deployer.address);
  
    const MyContract = await ethers.getContractFactory("Operator");
    const myContract = await MyContract.deploy("0xbe8582a2aAD675b6909732d1cB69dc5Ac15744dD","0x8A91DC2D28b689474298D91899f0c1baF62cB85b");
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
  