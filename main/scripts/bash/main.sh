#!/bin/bash

# Function to generate accounts
create_accounts() {
    echo "Generating accounts..."
    miners=$1
    clients=$2
    data_dir=$3  # Default data directory
    password_length=$4  # Default password length
    local bc_script="../../networks/middlewares/create_accounts.py"
    echo $miners
    # Remove existing data directory
    rm -rf "$data_dir"

    # Call geth to generate accounts
    python3 $bc_script --miners $miners --clients $clients --data-dir $data_dir --password-length $password_length
    echo $data_dir
}


# Function to update genesis files
update_accounts_balance() {
    echo "Updating genesis files..."
    # genesis is the path to the directory containing the genesis file
    genesis=$1 # Default genesis path
    balance=$2  # Default balance
    data_dir=$3  # Default data directory for geth clients
    consensus="poa"
    local update_accounts_balance_script="../../networks/middlewares/update_accounts_balance.py"

    # Ensure datadir is defined if not provided as an argument
    if [[ -z "$data_dir" ]]; then
        echo "Error: a datadir for geth client should be provided"
        exit 1
    fi
    src="${genesis}/genesis_poa.json"
    dst="${data_dir}/genesis_poa.json"
    # Call the update_genesis function from bc python script
    python3 $update_accounts_balance_script --src $src --dst $dst --consensus $consensus --balance $balance --data-dir $data_dir
    if [[ $? -ne 0 ]]; then  # Check for errors
    echo "Error updating genesis file for consensus: $consensus"
    exit 1
    fi

}

# Function to build Docker images
build_images() {
  # Pull the base image at the beginning of the process
  #docker pull ethereum/client-go:v1.10.16
  
  bcNode_dockerfile="../../networks/docker/Dockerfile.bcNode"
  bfl_dockerfile="../../networks/docker/Dockerfile.flNode"
  task_publisher_dockerfile="../../networks/docker/Dockerfile.taskPublisher"
  admin_dockerfile="../../networks/docker/Dockerfile.adminNode"

  # Build Docker image for geth node
  # "../.." When you specify a directory as the build context, Docker only has access to files and directories within that context and its subdirectories
#   docker build -f "$bcNode_dockerfile" -t "bc-node" "../.."

  # Build Docker image for bfl node
  docker build -f "$bfl_dockerfile" -t "fl-node" "../.."
    # Build Docker image for the task publisher
  docker build -f "$task_publisher_dockerfile" -t "task-publisher-node" "../.."
    # Build Docker image for admin node
  docker build -f "$admin_dockerfile" -t "admin-node" "../.."
}

# create a docker network
create_docker_network() {
    network_name=$1
    driver=$2
    subnet=$3

    docker network create \
        --driver=$driver \
        --subnet=$subnet \
        $network_name
}

## launch docker container , the ones establishing the BC network
start_bc_containers(){
    local miners=$1  # Accept MINERS as an argument
    local networkid=$2  # Accept NETWORK_ID as an argument
    local sharding=$3  # Accept sharding as an argument
    local blockchain_yml="../../networks/docker-compose/bc.yml"  # full path to bc.yml
    NETWORK_ID=$networkid MINERS=$miners SHARDING=$sharding docker-compose -f $blockchain_yml -p one up 
    ##--build
}

# Function to connect peers
connect_peers() {
    echo "Connecting peers..."
    local network=$1
    local connect_peers_script="../../networks/middlewares/connect_peers.py"
    python3 $connect_peers_script --network $network

}

# Function to deploy contract
deploy_smart_contract() {
    echo "Deploying contract..."
    data_dir="../../networks/blockchain/datadir"
    local deploy_contract_script="../../networks/middlewares/deploy_smart_contracts.py"
    python3 $deploy_contract_script -d $data_dir

}

# Function to split data between clients
split_data() {
    echo "Splitting data ..."
    local dataset=$1
    local n_parties=$2
    local partition=$3
    local beta=$4
    local datadir=$5
    echo $n_parties
    local split_data_script="../../FederatedLearning/data_manipulation//splitData.py"
    python3 $split_data_script --dataset $dataset --n_parties $n_parties --partition $partition --beta $beta --datadir $datadir 

}

# launch task publisher container 
# Function to launch a Docker container
launch_task_publisher() {
  # Check if required arguments are provided
  if [ $# -lt 3 ]; then
    echo "Usage: $0 <image_name> <container_name> <command>"
    echo "  * image_name: The name of the Docker image to use."
    echo "  * container_name: The name to assign to the container."
    return 1
  fi

  # Get arguments
  image_name="$1"
  container_name="$2"
  shift 2  # Shift arguments to access the remaining ones for the command

  # Build remaining arguments for the docker run command
  docker_run_args="-d --name $container_name $image_name"

  # Add optional command argument if provided
  if [ $# -gt 0 ]; then
    docker_run_args="$docker_run_args '$*'"  # Use double quotes to handle spaces in the command
  fi

  # Run the docker run command
  docker run $docker_run_args

  # Print success message
  echo "Container '$container_name' launched successfully."
}


# launch federated learning containers
start_fl_containers(){
    echo "Launching Federated learning containers..."
    local contract_address=$1
    local abi=$2
    local abi_file=$3
    local contract_address_reputation=$4
    local abi_reputation=$5
    local abi_file_reputation=$6
    local contract_address_oracle=$7
    local abi_oracle=$8
    local abi_file_oracle=$9
    local trainers=${10}
    local admins_number=${11}
    local evaluation_name=${12}
    local task=${13}
    echo $task
    local fl_yml="../../networks/docker-compose/fl.yml"  # full path to fl.yml
    CONTRACT=$contract_address ABI=$abi ABI_FILE=$abi_file CONTRACT_REPUTATION=$contract_address_reputation ABI_REP=$abi_reputation ABI_FILE_REP=$abi_file_reputation CONTRACT_ORACLE=$contract_address_oracle ABI_ORACLE=$abi_oracle ABI_FILE_ORACLE=$abi_file_oracle ADMINS=$admins_number CLIENTS=$trainers TASKPUBLISHERS=1 EVALUATION_NAME=$evaluation_name TASK=$task docker-compose -f $fl_yml -p federated_learning up --remove-orphans 
    # CONTRACT=$contract_address ABI=$abi ABI_FILE=$abi_file CONTRACT_REPUTATION=$contract_address_reputation ABI_REP=$abi_reputation ABI_FILE_REP=$abi_file_reputation CONTRACT_ORACLE=$contract_address_oracle ABI_ORACLE=$abi_oracle ABI_FILE_ORACLE=$abi_file_oracle ADMINS=$admins_number AGGREGATORS=$aggregators CLIENTS=$trainers TASKPUBLISHERS=1 EVALUATION_NAME=$evaluation_name TASK=$task docker-compose -f $fl_yml -p federated_learning up --remove-orphans 
    # CONTRACT= MINERS=2 AGGREGATORS=1 CLIENTS=3 TASK=$task ABI="NoScore" TASKPUBLISHERS=1 EVALUATION_NAME="group_instance_deletion_based_evaluation" ABI_FILE="NoScoring" ABI1="APIConsumer" ABI_FILE1="APIconsumer" CONTRACT1="0x1b7fc98A7e076bE10F6E864026cccD74eF0625eb" ADMINS=1 docker-compose -f $fl_yml -p federated_learning up --remove-orphans 

}

# create @ and password for a new task publisher
create_account_task_publisher(){
    echo "Creating account for a new task publisher..."
    data_dir=$1
    password_length=$2
    local file_path="/home/meryem/stage/pfe/truffle/networks/middlewares/create_account_task_publisher.py"
    python3 $file_path --data-dir $data_dir --password-length $password_length


}

# launch task publisher container
start_task_publisher_containers(){
    echo "Launching task publisher container..."
    local contract_address=$1
    local task_publisher_numbers=$2
    local abi=$3
    local abi_file=$4
    local rounds=$5
    local requiredTrainers=$6
    local requiredAggregators=$7
    local task_yml="../../networks/docker-compose/taskp.yml"  # full path to taskp.yml
    CONTRACT=$contract_address TASKPUBLISHERS=$task_publisher_numbers ABI=$abi ROUNDS=$rounds ABI_FILE=$abi_file TRAINERS=$requiredTrainers AGGREGATORS=$requiredAggregators docker-compose -f $task_yml -p task up --remove-orphans 
}




# launch admin container
start_admins_containers(){
    echo "Launching admin container..."
    local contract_address=$1
    local admins_number=$2
    local abi=$3
    local abi_file=$4
    local oracle_node_address=$5
    
    echo $contract_address
    local admin_yml="../../networks/docker-compose/admin.yml"  # full path to admin.yml
    CONTRACT_ORACLE=$contract_address ADMINS=$admins_number ABI_ORACLE=$abi ABI_FILE_ORACLE=$abi_file ORACLE_NODE_ADDRESS=$oracle_node_address docker-compose -f $admin_yml -p admin up --remove-orphans 
    # CONTRACT=$contract_address ADMINS=$admins_number MINERS=$miners TASK=$task ABI=$abi ABI_FILE=$abi_file docker-compose -f $admin_yml -p admin up --remove-orphans 
}


# launch admin container
start_admin_shard_containers(){
    echo "Launching admin shard container..."
    local admin_shard_yml="../../networks/docker-compose/admin_shard.yml"  # full path to admin_shard.yml
    docker-compose -f $admin_shard_yml -p adminShard up --remove-orphans 
    # CONTRACT=$contract_address ADMINS=$admins_number MINERS=$miners TASK=$task ABI=$abi ABI_FILE=$abi_file docker-compose -f $admin_yml -p admin up --remove-orphans 
}

# Contribution measurement methods 
# group_instance_deletion_based_evaluation
# similarity_based_evaluation
# marginal_gain_based_evaluation

# Main script logic
echo "Starting script..."

# Call functions 
#create_accounts 10 10 "../../networks/blockchain/datadir" 15
#create_account_task_publisher "../../networks/blockchain/datadir" 15 
#update_accounts_balance "../../networks/blockchain" "1000000000000000000000" "../../networks/blockchain/datadir"
#build_images 
#create_docker_network "BCFL" "bridge" "172.16.254.0/20"

# the & allows the functionto be run in background , this way I can see the connect_peers function outputs  start_bc_containers 2 192442 &

#start_bc_containers 10 4444 false
#wait
#connect_peers 40eac362b46c
#deploy_smart_contract

#split_data mnist 1000 noniid-labeldir 0.5 ../../FederatedLearning/data_manipulation/data/  

#launch_task_publisher task-publisher-node task-publisher-nodes



    
    


start_fl_containers 0xDe9BFE17987aF53F4b9A1d09a2431f544ECd9EA9 NoScore NoScoring 0xA1F17BcB2e696Cc2f01857Fef2f15e39A15738E7 ManageReputation manageRep  0x9EB53A176a8a92117B98dedaAD0979C9671f2e27 APIConsumer APIconsumer 8 1 similarity 0  #  taskContract abiTask abiFileTask oracleContract abiOracle abiFileOracle trainers admins evaluation_method_name taskId


# real task publishing script
#start_task_publisher_containers 0xDe9BFE17987aF53F4b9A1d09a2431f544ECd9EA9 1 NoScore NoScoring 6 7 1 # contractAddress tpNumbers abi abiFile roundsNumber requiredTrainers requiredAggs




#authorize the senders in operator contract
#start_admins_containers 0xb0F5C5dCcd4Acec2d73f90E5003eEE620835573F 1 Operator Operator 0xEA4F59f0886C068968d3bFd9BD1a79Db35649Ac6    # admins_number abi abi_file oracle_node_address
 
#start_admin_shard_containers

# to run the oracles 
#docker-compose -f $fl_yml -p oracles up 


echo "Script execution completed."

