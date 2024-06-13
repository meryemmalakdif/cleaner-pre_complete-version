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


ACCOUNT="0x62722e67330665aEA8eb2857c57F4693B5B58EaD"
PASSWORD="2IEv6i98E6t2BQL"




# ip@ of a miner => will be used as a provider for the client 




#PROVIDER=$(dig bfl-geth-miner-$PRVINDEX +short)


python admin_shard.py \
  --genesis /root/shards/common_genesis_poa.json \
  --accounts /root/shards/accounts.json \






