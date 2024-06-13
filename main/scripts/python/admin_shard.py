import os
import json
import click
import subprocess
import shutil
import re
import random
# Get the path to the FederatedLearning directory relative to my_script.py



@click.command()
@click.option('--genesis', default='', help='contract abi file')
@click.option('--accounts', default='', help='contract abi file')
# maybe later on u need to add the task id , for now makech 
def main(genesis, accounts):
    shard = 1

    # directory = "/root/shards"
    # # Loop through all entries in the directory to delete all the shards folder 
    # for entry in os.listdir(directory):
    #     # Construct the full path of the entry
    #     entry_path = os.path.join(directory, entry)
        

        # # Check if the entry is a file
        # if os.path.isfile(entry_path):
        #     try:
        #         # Remove the file
        #         os.remove(entry_path)
        #         print(f"Deleted file: {entry_path}")
        #     except Exception as e:
        #         print(f"Error deleting file {entry_path}: {e}")


        # # Check if the entry is a directory
        # if os.path.isdir(entry_path):
        #     try:
        #         # Remove the directory and its contents recursively
        #         shutil.rmtree(entry_path)
        #         print(f"Deleted directory: {entry_path}")
        #     except Exception as e:
        #         print(f"Error deleting directory {entry_path}: {e}")



    src_dir_geth = "/root/mainChain/geth"
    src_dir_keystore = "/root/mainChain/keystore"
    
  
    # Get a list of all files in the directory
    all_files_geth = os.listdir(src_dir_geth)
    all_files_keystore = os.listdir(src_dir_keystore)

    # Define the list of patterns
    patterns = ["0xA1A23284B276aE7E000274871F40E053a12966b0", "0x4a3A897655123BAd9Ee79EC6622b545B7226C232","0xfBE69718252CDAC5C166Be5747F184958Ee380e9"]

    rpc_endpoint = random.randint(0,len(patterns)-1)

    # Filter the files using a list comprehension and regular expressions
    filtered_files_geth = [file for file in all_files_geth if any(re.search(pattern, file) for pattern in patterns)] 
    filtered_files_keystore = [file for file in all_files_keystore if any(re.search(pattern[2:], file, re.IGNORECASE) for pattern in patterns)]  

    dest_dir_geth = f"/root/shards/shard_{shard}/geth"
    dest_dir_keystore = f"/root/shards/shard_{shard}/keystore"
    new_folder_path = f"/root/shards/shard_{shard}"


    # Create the destination directory if it doesn't exist
    os.makedirs(dest_dir_geth, exist_ok=True)
    os.makedirs(dest_dir_keystore, exist_ok=True)

    # copy the filtered files to shard_i/geth
    for index , file in enumerate(filtered_files_geth):
        src_path = os.path.join(src_dir_geth, file)
        if index == rpc_endpoint:
            dest_path = os.path.join(dest_dir_geth, "nodekey_owner")
        else:
            dest_path = os.path.join(dest_dir_geth, file)
            
        try:
            # Copy the file to the destination directory
            shutil.copy2(src_path, dest_path)
        except Exception as e:
            print(f"Error copying {src_path}: {e}")

    # copy the filtered files to shard_i/keystore
    for file in filtered_files_keystore:
        src_path = os.path.join(src_dir_keystore, file)
        dest_path = os.path.join(dest_dir_keystore, file)
        try:
            # Copy the file to the destination directory
            shutil.copy2(src_path, dest_path)
        except Exception as e:
            print(f"Error copying {src_path}: {e}")

    # Load the existing genesis file
    with open(genesis, 'r') as f:
       genesis_data = json.load(f)

    balance = "1000000000000000000000"
    # need to get the balance of the validator at the moment of the shard's creation
    
    # Define the new accounts and balances to add
    new_accounts = {account: {"balance": balance} for account in patterns}

    # Add the new accounts to the "alloc" section
    genesis_data["alloc"].update(new_accounts)

    # set the shard chain id
    genesis_data["config"]["chainId"] += 1 

    # Set the extraData field
    for account in patterns:
        genesis_data["extraData"] += account[2:]
    genesis_data["extraData"] += '0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    new_genesis = os.path.join(new_folder_path, "genesis_poa.json")

    # Save the updated genesis file
    with open(new_genesis, 'w') as f:
       json.dump(genesis_data, f, indent=2)

   


    with open(accounts, 'r') as f:
       accounts_data = json.load(f)
    # Filter the "miners" dictionary
    filtered_miners = {address: accounts_data["miners"][address] for address in patterns if (address in accounts_data["miners"] and address != patterns[rpc_endpoint]) }
    filtered_owner = {address: accounts_data["miners"][address] for address in patterns if (address in accounts_data["miners"] and address == patterns[rpc_endpoint]) }

    accounts_data["miners"] = filtered_miners
    accounts_data["owner"] = filtered_owner
    new_accounts = os.path.join(new_folder_path, "accounts.json")
        # Save the updated genesis file
    with open(new_accounts, 'w') as f:
       json.dump(accounts_data, f, indent=2)





    # container_id=run_and_output(f'docker ps')
    # docker stop "$CONTAINER_ID"
    # output = run_and_output(f'docker stop $(docker ps -q | xargs -n 1 docker inspect --format \'{{ .Name }}: {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}\' | grep \'172.16.240.3\' | cut -d\':\' -f1)') 
    

    # # Specify the directory path
    # directory = "/root/shards"


    # new_folder_name = "shard_7"

    # # Construct the full path for the new folder
    # new_folder_path = os.path.join(directory, new_folder_name)
    # print("yayyy ",new_folder_path)

    # try:
    #     # Create the new folder
    #     os.makedirs(new_folder_path)
    #     print(f"Folder '{new_folder_path}' created successfully.")
    # except FileExistsError:
    #     print(f"Folder '{new_folder_path}' already exists.")
    # except Exception as e:
    #     print(f"An error occurred while creating the folder: {e}")
  
    # # Construct the full path for the keystore folder
    # keystore_folder_path = os.path.join(new_folder_path, "keystore")

    # try:
    #     # Create the new folder
    #     os.makedirs(keystore_folder_path)
    #     print(f"Folder '{keystore_folder_path}' created successfully.")
    # except FileExistsError:
    #     print(f"Folder '{keystore_folder_path}' already exists.")
    # except Exception as e:
    #     print(f"An error occurred while creating the folder: {e}")

    # # Construct the full path for the geth folder
    # geth_folder_path = os.path.join(new_folder_path, "geth")

    # try:
    #     # Create the new folder
    #     os.makedirs(geth_folder_path)
    #     print(f"Folder '{geth_folder_path}' created successfully.")
    # except FileExistsError:
    #     print(f"Folder '{geth_folder_path}' already exists.")
    # except Exception as e:
    #     print(f"An error occurred while creating the folder: {e}")




    
    #contract = smart_contract_functions.Contract(logs, provider, abi, account, passphrase, contract)
   

    # while True:
    #     captured_event = None  # Initialize a variable to hold the event data outside the loop
    #     event_filter = contract.contract.events.ShardNodes.create_filter(fromBlock='latest') 
    #     while True:
    #         new_entries = event_filter.get_new_entries()
    #         if new_entries:  # Check if there are new entries
    #             captured_event = new_entries[0]  # Save the first event (assuming you're interested in the first one)
    #             break  # Exit the loop after capturing the event

    #     if captured_event:
    #         shard_ip_addresses = captured_event['args']['ipAddresses']
            

def run_and_output(command):
  p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
  (stdout, stderr) = p.communicate()
  p_status = p.wait()

  if p_status != 0:
    print(stderr)
    exit(p_status)

  return stdout.decode()          

main()
