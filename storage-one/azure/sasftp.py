import subprocess
import json
import time

class SaSftp:

    def __init__(self,
                subscription_id,
                resource_group_name,
                storage_acc_name,
                storage_cont_name,
                local_user_name ) -> None:
      self.azure_subscription_id = subscription_id
      self.azure_resource_group = resource_group_name #"rg-terraform-sftp-storage_2"
      self.azure_storage_account = storage_acc_name #"sasftptestrig2"
      self.azure_storage_container_name = storage_cont_name #"sftpcont"+str(uuid.uuid4())
      self.local_username = local_user_name #"user"+str(int(time.time()))

    def enable_sftp(self):
        # enable sftp
        print("Enabling SFTP")       

        az_cli_command_set_sub ="az account set --subscription {}".format(self.azure_subscription_id)

        az_cli_command_enable_sftp = "az storage account update -g {} -n {} --enable-sftp=true".format(self.azure_resource_group, self.azure_storage_account)

        subprocess.run(az_cli_command_set_sub, shell=True, capture_output=True, text=True)

        results = subprocess.run(az_cli_command_enable_sftp, shell=True, capture_output=True, text=True)        
        json_response_sftp_enable = json.loads(results.stdout)
        if not json_response_sftp_enable["isSftpEnabled"]:
            raise ValueError("SFTP was not enabled")
        
    def create_container(self):
        # enable_sftp()
        # create container
        print("Creating container")        

        az_cli_command_create_container = "az storage container create -n {} --account-name {} --auth-mode login".format(self.azure_storage_container_name, self.azure_storage_account)
        results = subprocess.run(az_cli_command_create_container, shell=True, capture_output=True, text=True)        
        json_response_container_create = json.loads(results.stdout)
        if not json_response_container_create["created"]:
            raise ValueError("Container was not created")
        
    def create_local_user(self):
        # create_container()
        # create local user
        # User name must be between 3 and 64 characters long and can only contain lowercase letters and numbers.
        print("Creating local user")
        
        az_cli_command_create_local_user = "az storage account local-user create --account-name {} -g {} -n {} --home-directory {} --permission-scope permissions=rwldc service=blob resource-name={} --has-ssh-password true".format(self.azure_storage_account, self.azure_resource_group, self.local_username, self.azure_storage_container_name, self.azure_storage_container_name)

        results = subprocess.run(az_cli_command_create_local_user, shell=True, capture_output=True, text=True) 
        json_response_local_user_create = json.loads(results.stdout)
        if not json_response_local_user_create["hasSshPassword"]:
            raise ValueError("Local user was not created")

    def regenerate_password(self):
        # regenerate password
        # create_local_user()
        print("Regenerating password")
        az_cli_command_regen_pwd = "az storage account local-user regenerate-password --account-name {} -g {} -n {}".format(self.azure_storage_account, self.azure_resource_group, self.local_username)
        results = subprocess.run(az_cli_command_regen_pwd, shell=True, capture_output=True, text=True)
        json_response_password_regenerate = json.loads(results.stdout)
        if not json_response_password_regenerate["sshPassword"]:
            raise ValueError("Password was not regenerated")
    
        return json_response_password_regenerate["sshPassword"]

    def disable_sftp(self):
        # disable sftp
        print("Disabling SFTP")
        az_cli_command_disable_sftp = "az storage account update -g {} -n {} --enable-sftp=false".format(self.azure_resource_group, self.azure_storage_account)
        results = subprocess.run(az_cli_command_disable_sftp, shell=True, capture_output=True, text=True)
        json_response_sftp_disable = json.loads(results.stdout)
        if json_response_sftp_disable["isSftpEnabled"]:
            raise ValueError("SFTP was not disabled")

    def delete_local_user(self):

        print("Deleting local user")
        az_cli_command_delete_local_user = "az storage account local-user delete --account-name {} -g {} -n {}".format(self.azure_storage_account, self.azure_resource_group, self.local_username)
        subprocess.run(az_cli_command_delete_local_user, shell=True, capture_output=True, text=True)
        
        

    def delete_container(self):
        print("Deleting container") #az storage container delete --account-key 00000000 --account-name MyAccount --name mycontainer
        az_cli_command_delete_container = "az storage container delete -n {} --account-name {}".format(self.azure_storage_container_name, self.azure_storage_account)
        results = subprocess.run(az_cli_command_delete_container, shell=True, capture_output=True, text=True)
        
        json_response_container_delete = json.loads(results.stdout)
        if not json_response_container_delete["deleted"]:
            raise ValueError("Container was not deleted")
        