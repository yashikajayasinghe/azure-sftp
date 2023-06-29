import paramiko
import os

# Create an SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

azure_ssh_pwd = os.environ.get("AZURE_SSH_PWD")
azure_ssh_u_name = os.environ.get("AZURE_SSH_UNAME")
azure_sftp_host_name = os.environ.get("AZURE_SFTP_HOSTNAME")

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










# connection_string = "DefaultEndpointsProtocol=https;AccountName=xxxx;AccountKey=xxxx;EndpointSuffix=core.windows.net"
# service = ShareServiceClient.from_connection_string(conn_str=connection_string)
# service = ShareServiceClient(account_url="https://<my-storage-account-name>.file.core.windows.net/", credential=credential)

