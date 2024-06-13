import { HardhatUserConfig } from "hardhat/config";


require("@nomiclabs/hardhat-ethers");
require("@nomicfoundation/hardhat-verify");

import "@matterlabs/hardhat-zksync";
import "@matterlabs/hardhat-zksync-deploy";
import "@matterlabs/hardhat-zksync-solc";

const config: HardhatUserConfig = {
  defaultNetwork: "dockerizedNode",
  networks: {
    dockerizedNode: {
      url: "http://127.0.0.1:3050",
      ethNetwork: "http://127.0.0.1:8545",
      zksync: true,
    },
    inMemoryNode: {
      url: "http://127.0.0.1:8011",
      ethNetwork: "localhost", // in-memory node doesn't support eth node; removing this line will cause an error
      zksync: true,
    },
    hardhat: {
      zksync: true,
    },
  },
  zksolc: {
    version: "latest",
    settings: {
      // find all available options in the official documentation
      // https://era.zksync.io/docs/tools/hardhat/hardhat-zksync-solc.html#configuration
        libraries: {
              "contracts/Math.sol": {
                "Math": "0x111C3E89Ce80e62EE88318C2804920D4c96f92bb"
              }
            }
    },
  },
  solidity: {
    version: "0.8.17",
  },
};

export default config;
