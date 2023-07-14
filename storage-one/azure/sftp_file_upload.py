import subprocess
import json
import uuid
import paramiko
import time
import os


azure_subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
azure_resource_group = "rg-terraform-sftp-storage_2"
azure_storage_account = "sasftptestrig2"
azure_storage_container_name = "sftpcont"+str(uuid.uuid4())
local_username = "user"+str(int(time.time()))

#TODO : Remove wait time

def enable_sftp():
    # enable sftp
    print("Enabling SFTP")
    

    az_cli_command_set_sub ="az account set --subscription {}".format(azure_subscription_id)

    az_cli_command_enable_sftp = "az storage account update -g {} -n {} --enable-sftp=true".format(azure_resource_group, azure_storage_account)

    subprocess.run(az_cli_command_set_sub, shell=True, capture_output=True, text=True)

    results = subprocess.run(az_cli_command_enable_sftp, shell=True, capture_output=True, text=True)
    time.sleep(20)
    json_response_sftp_enable = json.loads(results.stdout)
    if not json_response_sftp_enable["isSftpEnabled"]:
        raise ValueError("SFTP was not enabled")
    
def create_container():
    enable_sftp()
    # create container
    print("Creating container")
    

    az_cli_command_create_container = "az storage container create -n {} --account-name {} --auth-mode login".format(azure_storage_container_name, azure_storage_account)
    results = subprocess.run(az_cli_command_create_container, shell=True, capture_output=True, text=True)
    time.sleep(20)
    json_response_container_create = json.loads(results.stdout)
    if not json_response_container_create["created"]:
        raise ValueError("Container was not created")
    
def create_local_user():
    create_container()
    # create local user
    # User name must be between 3 and 64 characters long and can only contain lowercase letters and numbers.
    print("Creating local user")
    
    az_cli_command_create_local_user = "az storage account local-user create --account-name {} -g {} -n {} --home-directory {} --permission-scope permissions=rwldc service=blob resource-name={} --has-ssh-password true".format(azure_storage_account, azure_resource_group, local_username, azure_storage_container_name, azure_storage_container_name)

    results = subprocess.run(az_cli_command_create_local_user, shell=True, capture_output=True, text=True)
    time.sleep(20)
    json_response_local_user_create = json.loads(results.stdout)
    if not json_response_local_user_create["hasSshPassword"]:
        raise ValueError("Local user was not created")

def regenerate_password():
    # regenerate password
    create_local_user()
    print("Regenerating password")
    az_cli_command_regen_pwd = "az storage account local-user regenerate-password --account-name {} -g {} -n {}".format(azure_storage_account, azure_resource_group, local_username)
    results = subprocess.run(az_cli_command_regen_pwd, shell=True, capture_output=True, text=True)
    time.sleep(20)
    json_response_password_regenerate = json.loads(results.stdout)
    if not json_response_password_regenerate["sshPassword"]:
        raise ValueError("Password was not regenerated")
   
    return json_response_password_regenerate["sshPassword"]

def disable_sftp():
    # disable sftp
    print("Disabling SFTP")
    az_cli_command_disable_sftp = "az storage account update -g {} -n {} --enable-sftp=false".format(azure_resource_group, azure_storage_account)
    results = subprocess.run(az_cli_command_disable_sftp, shell=True, capture_output=True, text=True)
    time.sleep(20)
    json_response_sftp_disable = json.loads(results.stdout)
    if json_response_sftp_disable["isSftpEnabled"]:
        raise ValueError("SFTP was not disabled")

def delete_local_user():

    print("Deleting local user")
    az_cli_command_delete_local_user = "az storage account local-user delete --account-name {} -g {} -n {}".format(azure_storage_account, azure_resource_group, local_username)
    subprocess.run(az_cli_command_delete_local_user, shell=True, capture_output=True, text=True)
    time.sleep(20)
    

def delete_container():
    print("Deleting container") #az storage container delete --account-key 00000000 --account-name MyAccount --name mycontainer
    az_cli_command_delete_container = "az storage container delete -n {} --account-name {}".format(azure_storage_container_name, azure_storage_account)
    results = subprocess.run(az_cli_command_delete_container, shell=True, capture_output=True, text=True)
    time.sleep(20)
    json_response_container_delete = json.loads(results.stdout)
    if not json_response_container_delete["deleted"]:
        raise ValueError("Container was not deleted")
    
def upload_file():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    azure_ssh_pwd = regenerate_password() #os.environ.get("AZURE_SSH_PWD")
    azure_ssh_u_name = f"{azure_storage_account}.{local_username}" #os.environ.get("AZURE_SSH_UNAME")
    azure_sftp_host_name = azure_storage_account+".blob.core.windows.net" #os.environ.get("AZURE_SFTP_HOSTNAME")

    # Connect to the SFTP server
    ssh.connect(azure_sftp_host_name , username=azure_ssh_u_name, password=azure_ssh_pwd)           

    # Open an SFTP session
    sftp = ssh.open_sftp()

    # Perform SFTP operations
    # For example, you can download a file
    local_file_path = 'file.txt'
    remote_file_path = '/file.txt'
    sftp.put(local_file_path, remote_file_path)

    # Close the SFTP session and SSH connection
    sftp.close()
    ssh.close()

# NEED TO DELETE LOCAL USER AND CONTAINER
    disable_sftp()


upload_file()
