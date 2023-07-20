from sasftp import SaSftp
import os
import paramiko
import time
import uuid
import pytest

@pytest.fixture(scope="module")
def setup_sftp(): #input request fixture

    subscription_id = getattr(os.environ, "AZURE_SUBSCRIPTION_ID", None)
    resource_group_name = getattr(os.environ, "AZURE_RESOURCE_GROUP_NAME", "rg-terraform-sftp-storage_2")
    storage_acc_name = getattr(os.environ, "AZURE_STORAGE_ACCOUNT_NAME", "sasftptestrig2")
    storage_cont_name = getattr(os.environ, "AZURE_STORAGE_CONTAINER_NAME", "sftpcont"+str(uuid.uuid4()))
    local_user_name = getattr(os.environ, "AZURE_LOCAL_USER_NAME", "user"+str(int(time.time())))

    sftp_conn = SaSftp(subscription_id = subscription_id, 
                        resource_group_name = resource_group_name,
                        storage_acc_name = storage_acc_name,
                        storage_cont_name = storage_cont_name,
                        local_user_name = local_user_name)
                        
    sftp_conn.enable_sftp()
    sftp_conn.create_container()
    sftp_conn.create_local_user()
    new_pwd = sftp_conn.regenerate_password()

    hostname = sftp_conn.azure_storage_account+".blob.core.windows.net"
    username = storage_acc_name+"."+local_user_name

    yield {"hostname":hostname, "user_name":username, "pwd":new_pwd}
    sftp_conn.disable_sftp()
    sftp_conn.delete_container()
    sftp_conn.delete_local_user()


def test_upload_file(setup_sftp):
    # Create an SSH client
    sftp_connection_info = setup_sftp
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    
    # Connect to the SFTP server
    print("Connecting to SFTP server")
    print("Connecting to SFTP server"+sftp_connection_info["hostname"])
    time.sleep(10)
    ssh.connect(hostname = sftp_connection_info["hostname"] , username=sftp_connection_info["user_name"], password=sftp_connection_info["pwd"], timeout=20)           

    # Open an SFTP session
    sftp = ssh.open_sftp()

    # Perform SFTP operations
    
    local_file_path = 'file.txt'
    remote_file_path = '/file.txt'
    sftp.put(local_file_path, remote_file_path)

    # Close the SFTP session and SSH connection
    sftp.close()
    ssh.close()
    assert True


