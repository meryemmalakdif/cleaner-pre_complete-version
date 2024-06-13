#!/bin/sh
IP=$(ifconfig eth0 | grep 'inet' | awk '{print $2}' | sed 's/addr://')
echo "IP: $IP"
INDEX=$(dig -x $IP +short | sed 's/[^0-9]*//g')
echo "INDEX: $INDEX"
ACCOUNT=$(jq -r '.taskpublishers' accounts.json | jq 'keys_unsorted' | jq -r "nth($((INDEX-1)))")
echo "ACCOUNT: $ACCOUNT"
PRIVATEKEY=$(jq -r '.taskpublishers' accounts.json | jq -r ".[\"$ACCOUNT\"]")
echo "PRIVATEKEY: $PRIVATEKEY"

IPADDRESSZKSYNC=$(dig zksync-local-node_zksync_1 +short)

IPADDRESS=$(dig zksync-local-node_geth_1 +short)



PROVIDER="${IPADDRESS}:8545"

PROVIDERZKSYNC="${IPADDRESSZKSYNC}:3050"






python task_publisher.py \
  --provider "http://$PROVIDERZKSYNC" \
  --abi /root/abi.json \
  --ipfs $IPFS_API \
  --account $ACCOUNT \
  --passphrase $PRIVATEKEY \
  --contract $CONTRACT \
  --rounds $ROUNDS \
  --required_trainers_number $TRAINERS \
  --required_aggregators_number $AGGREGATORS \
  





