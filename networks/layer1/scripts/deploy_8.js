async function main() {
    const [deployer] = await ethers.getSigners();
    console.log("Deploying contracts with the account:", deployer.address);
  
    const MyContract = await ethers.getContractFactory("ManageReputation"
    , {
      libraries: {
        Math: "0xA5dCc42196aFC9dAd9c42B4F3Db76AcD10fCb750",
      },
    }
    );

    
    const myContract = await MyContract.deploy("0x0BB37E76CCfc1E37E0d2E28866Da91274e58c215","0x8DC59043260465B5DdF207A3eB817D4846039665");
    const addressi=  await myContract.getAddress();
    console.log("Deployed address:" + myContract.address);
    console.log("manage reputation contract deployed to:", addressi);
  }


  
  main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
    });
  