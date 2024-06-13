#!/bin/sh
IP=$(ifconfig eth0 | grep 'inet' | awk '{print $2}' | sed 's/addr://')
echo "IP: $IP"
INDEX=$(dig -x $IP +short | sed 's/[^0-9]*//g')
echo "INDEX: $INDEX"
ACCOUNT=$(jq -r '.clients' accounts.json | jq 'keys_unsorted' | jq -r "nth($((INDEX-1)))")
echo "ACCOUNT: $ACCOUNT"
PRIVATEKEY=$(jq -r '.clients' accounts.json | jq -r ".[\"$ACCOUNT\"]")
echo "PASSWORD: $PRIVATEKEY"

IPADDRESSZKSYNC=$(dig zksync-local-node_zksync_1 +short)

IPADDRESS=$(dig zksync-local-node_geth_1 +short)



PROVIDER="${IPADDRESS}:8545"

PROVIDERZKSYNC="${IPADDRESSZKSYNC}:3050"



python aggregator.py \
  --provider "http://$PROVIDERZKSYNC" \
  --abi /root/abi.json \
  --ipfs $IPFS_API \
  --account $ACCOUNT \
  --passphrase $PRIVATEKEY \
  --contract $CONTRACT \
  --task $TASK \
  --validation /root/dataset/validation/party_0.npz \





