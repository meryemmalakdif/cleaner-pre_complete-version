#!/bin/sh
# IP=$(ifconfig eth0 | grep 'inet' | awk '{print $2}' | sed 's/addr://')
# echo "IP: $IP"
# INDEX=$(dig -x $IP +short | sed 's/[^0-9]*//g')
# echo "INDEX: $INDEX"
# ACCOUNT=$(jq -r '.clients' accounts.json | jq 'keys_unsorted' | jq -r "nth($((INDEX-1)))")
# echo "ACCOUNT: $ACCOUNT"
# PASSWORD=$(jq -r '.clients' accounts.json | jq -r ".[\"$ACCOUNT\"]")
# echo "PASSWORD: $PASSWORD"

# PRVINDEX=$((INDEX % MINERS))
# if [ "$PRVINDEX" -eq "0" ]; then
#   PRVINDEX=$MINERS
# fi

# PROVIDER=$(dig one_validator_$PRVINDEX +short)
# #PROVIDER=$(dig local-setup_reth_1 +short)
# #echo "Miner s ID: $PRVINDEX"
# echo "Miner s ip @: $PROVIDER"


# ACCOUNT="0x62722e67330665aEA8eb2857c57F4693B5B58EaD"
# PASSWORD="2IEv6i98E6t2BQL"




# # ip@ of a miner => will be used as a provider for the client 




# #PROVIDER=$(dig bfl-geth-miner-$PRVINDEX +short)


IPADDRESSZKSYNC=$(dig zksync-local-node_zksync_1 +short)

IPADDRESS=$(dig zksync-local-node_geth_1 +short)



PROVIDER="${IPADDRESS}:8545"

PROVIDERZKSYNC="${IPADDRESSZKSYNC}:3050"


# PRIVATEKEY="0x3eb15da85647edd9a1159a4a13b9e7c56877c4eb33f614546d4db06a51868b1c"

# ACCOUNT="0xE90E12261CCb0F3F7976Ae611A29e84a6A85f424"

PRIVATEKEY="0xe20eb92b34a3c5bd2ef0802a4bc443a90e73fc4a0edc4781446d7b22a44cc5d8"

ACCOUNT="0x8A91DC2D28b689474298D91899f0c1baF62cB85b"


python admin_authorize.py \
  --provider_layer1 "http://$PROVIDER" \
  --abi_oracle /root/abi_operator.json \
  --account $ACCOUNT \
  --passphrase $PRIVATEKEY \
  --contract_oracle $CONTRACT_ORACLE \
  --oracle_node $ORACLE_NODE_ADDRESS \

  

  






